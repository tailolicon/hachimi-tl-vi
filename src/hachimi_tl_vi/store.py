from __future__ import annotations

import json
from pathlib import Path
import sqlite3
from typing import Iterable, Iterator, Any

from .model import SourceEntry, Translation


SCHEMA = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS source_entries (
    uid TEXT PRIMARY KEY,
    kind TEXT NOT NULL,
    source_text TEXT NOT NULL,
    locator_json TEXT NOT NULL,
    context_json TEXT NOT NULL,
    fingerprint TEXT NOT NULL,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_source_kind ON source_entries(kind);
CREATE INDEX IF NOT EXISTS idx_source_fingerprint ON source_entries(fingerprint);

CREATE TABLE IF NOT EXISTS translations (
    fingerprint TEXT PRIMARY KEY,
    target_text TEXT NOT NULL,
    status TEXT NOT NULL,
    provider TEXT NOT NULL,
    model TEXT NOT NULL,
    qa_json TEXT NOT NULL DEFAULT '{}',
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS asset_documents (
    asset_path TEXT PRIMARY KEY,
    source_json TEXT NOT NULL,
    source_sha256 TEXT NOT NULL,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


class Store:
    def __init__(self, path: str | Path = "work/tlvi.db") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)

    def close(self) -> None:
        self.conn.close()

    def __enter__(self) -> "Store":
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()

    def upsert_entries(self, entries: Iterable[SourceEntry]) -> int:
        count = 0
        with self.conn:
            for e in entries:
                self.conn.execute(
                    """
                    INSERT INTO source_entries(uid, kind, source_text, locator_json, context_json, fingerprint, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(uid) DO UPDATE SET
                        kind=excluded.kind,
                        source_text=excluded.source_text,
                        locator_json=excluded.locator_json,
                        context_json=excluded.context_json,
                        fingerprint=excluded.fingerprint,
                        updated_at=CURRENT_TIMESTAMP
                    """,
                    (
                        e.uid,
                        e.kind,
                        e.source_text,
                        json.dumps(e.locator, ensure_ascii=False),
                        json.dumps(e.context, ensure_ascii=False),
                        e.fingerprint,
                    ),
                )
                count += 1
        return count

    def upsert_asset_document(self, asset_path: str, source_json: str, sha256: str) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT INTO asset_documents(asset_path, source_json, source_sha256, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(asset_path) DO UPDATE SET
                    source_json=excluded.source_json,
                    source_sha256=excluded.source_sha256,
                    updated_at=CURRENT_TIMESTAMP
                """,
                (asset_path, source_json, sha256),
            )

    def get_asset_documents(self) -> Iterator[tuple[str, Any]]:
        rows = self.conn.execute("SELECT asset_path, source_json FROM asset_documents ORDER BY asset_path")
        for row in rows:
            yield row["asset_path"], json.loads(row["source_json"])

    def pending_entries(self, kind: str | None = None, limit: int | None = None) -> list[SourceEntry]:
        sql = """
        SELECT s.* FROM source_entries s
        LEFT JOIN translations t ON t.fingerprint = s.fingerprint
        WHERE t.fingerprint IS NULL
        """
        params: list[Any] = []
        if kind:
            sql += " AND s.kind = ?"
            params.append(kind)
        sql += " ORDER BY s.kind, s.uid"
        if limit is not None:
            sql += " LIMIT ?"
            params.append(limit)
        return [self._row_to_entry(r) for r in self.conn.execute(sql, params)]

    def entries_with_translation(self, kind: str | None = None) -> Iterator[tuple[SourceEntry, Translation]]:
        sql = """
        SELECT s.*, t.target_text, t.status, t.provider, t.model, t.qa_json
        FROM source_entries s
        JOIN translations t ON t.fingerprint = s.fingerprint
        WHERE t.status IN ('translated', 'reviewed', 'manual')
        """
        params: list[Any] = []
        if kind:
            sql += " AND s.kind = ?"
            params.append(kind)
        sql += " ORDER BY s.kind, s.uid"
        for r in self.conn.execute(sql, params):
            entry = self._row_to_entry(r)
            tl = Translation(
                fingerprint=entry.fingerprint,
                target_text=r["target_text"],
                status=r["status"],
                provider=r["provider"],
                model=r["model"],
                qa=json.loads(r["qa_json"] or "{}"),
            )
            yield entry, tl

    def save_translation(self, translation: Translation) -> None:
        with self.conn:
            self.conn.execute(
                """
                INSERT INTO translations(fingerprint, target_text, status, provider, model, qa_json, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(fingerprint) DO UPDATE SET
                    target_text=excluded.target_text,
                    status=excluded.status,
                    provider=excluded.provider,
                    model=excluded.model,
                    qa_json=excluded.qa_json,
                    updated_at=CURRENT_TIMESTAMP
                """,
                (
                    translation.fingerprint,
                    translation.target_text,
                    translation.status,
                    translation.provider,
                    translation.model,
                    json.dumps(translation.qa, ensure_ascii=False),
                ),
            )

    def set_manual_translation(self, uid: str, text: str) -> None:
        row = self.conn.execute("SELECT * FROM source_entries WHERE uid = ?", (uid,)).fetchone()
        if not row:
            raise KeyError(uid)
        entry = self._row_to_entry(row)
        self.save_translation(
            Translation(entry.fingerprint, text, status="manual", provider="manual", model="manual")
        )

    def stats(self) -> dict[str, dict[str, int]]:
        result: dict[str, dict[str, int]] = {}
        rows = self.conn.execute(
            """
            SELECT s.kind AS kind,
                   COUNT(*) AS total,
                   SUM(CASE WHEN t.fingerprint IS NOT NULL THEN 1 ELSE 0 END) AS translated
            FROM source_entries s
            LEFT JOIN translations t ON t.fingerprint = s.fingerprint
            GROUP BY s.kind ORDER BY s.kind
            """
        )
        for r in rows:
            total = int(r["total"] or 0)
            translated = int(r["translated"] or 0)
            result[r["kind"]] = {"total": total, "translated": translated, "pending": total - translated}
        return result

    @staticmethod
    def _row_to_entry(r: sqlite3.Row) -> SourceEntry:
        return SourceEntry(
            uid=r["uid"],
            kind=r["kind"],
            source_text=r["source_text"],
            locator=json.loads(r["locator_json"]),
            context=json.loads(r["context_json"]),
        )

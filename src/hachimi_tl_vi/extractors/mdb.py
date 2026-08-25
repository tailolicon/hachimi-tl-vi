from __future__ import annotations

from pathlib import Path
import sqlite3
from typing import Iterable

from ..model import SourceEntry
from ..store import Store


TEXT_COLUMN_CANDIDATES = ("text", "message", "comment", "name", "description")


def _columns(conn: sqlite3.Connection, table: str) -> list[str]:
    return [str(r[1]) for r in conn.execute(f'PRAGMA table_info("{table}")')]


def _choose(columns: list[str], candidates: Iterable[str], *, table: str, role: str) -> str:
    lower = {c.lower(): c for c in columns}
    for candidate in candidates:
        if candidate.lower() in lower:
            return lower[candidate.lower()]
    raise ValueError(f"Cannot find {role} column in {table}. Columns: {columns}")


def _rows(conn: sqlite3.Connection, table: str, selected: list[str]):
    q = ", ".join(f'"{c}"' for c in selected)
    return conn.execute(f'SELECT {q} FROM "{table}"')


def import_master_mdb(path: str | Path, store: Store) -> dict[str, int]:
    path = Path(path)
    conn = sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True)
    out: dict[str, int] = {}
    try:
        tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}

        if "text_data" in tables:
            cols = _columns(conn, "text_data")
            cat = _choose(cols, ("category",), table="text_data", role="category")
            idx = _choose(cols, ("index", "id"), table="text_data", role="index")
            txt = _choose(cols, TEXT_COLUMN_CANDIDATES, table="text_data", role="text")
            entries = []
            for category, index, text in _rows(conn, "text_data", [cat, idx, txt]):
                if isinstance(text, str) and text.strip():
                    entries.append(SourceEntry(
                        uid=f"text_data:{category}:{index}", kind="text_data", source_text=text,
                        locator={"category": int(category), "index": int(index)},
                        context={"domain": "mdb", "table": "text_data", "category": int(category)},
                    ))
            out["text_data"] = store.upsert_entries(entries)

        if "character_system_text" in tables:
            cols = _columns(conn, "character_system_text")
            chara = _choose(cols, ("character_id", "chara_id"), table="character_system_text", role="character id")
            voice = _choose(cols, ("voice_id", "id", "index"), table="character_system_text", role="voice id")
            txt = _choose(cols, TEXT_COLUMN_CANDIDATES, table="character_system_text", role="text")
            entries = []
            for character_id, voice_id, text in _rows(conn, "character_system_text", [chara, voice, txt]):
                if isinstance(text, str) and text.strip():
                    entries.append(SourceEntry(
                        uid=f"character_system_text:{character_id}:{voice_id}", kind="character_system_text", source_text=text,
                        locator={"character_id": int(character_id), "voice_id": int(voice_id)},
                        context={"domain": "dialogue", "table": "character_system_text", "character_id": int(character_id)},
                    ))
            out["character_system_text"] = store.upsert_entries(entries)

        for table, kind in (
            ("race_jikkyo_comment", "race_jikkyo_comment"),
            ("race_jikkyo_message", "race_jikkyo_message"),
        ):
            if table not in tables:
                continue
            cols = _columns(conn, table)
            rid = _choose(cols, ("id", "index"), table=table, role="id")
            txt = _choose(cols, TEXT_COLUMN_CANDIDATES, table=table, role="text")
            entries = []
            for row_id, text in _rows(conn, table, [rid, txt]):
                if isinstance(text, str) and text.strip():
                    entries.append(SourceEntry(
                        uid=f"{kind}:{row_id}", kind=kind, source_text=text,
                        locator={"id": int(row_id)},
                        context={"domain": "race", "table": table},
                    ))
            out[kind] = store.upsert_entries(entries)
    finally:
        conn.close()
    return out

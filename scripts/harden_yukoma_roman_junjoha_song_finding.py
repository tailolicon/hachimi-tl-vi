from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

YUKOMA_ROMAN_JUNJOHA = {
    "id": "song.yukoma_roman_junjoha",
    "category": "song",
    "source_aliases": ["汤驹浪漫纯情派", "ゆこまロマン純情派"],
    "preferred": "Yukoma Roman Junjoha",
    "compact": [],
    "accepted": ["Yukoma Roman Junjoha"],
    "forbidden": ["汤驹浪漫纯情派", "ゆこまロマン純情派", "Khúc lãng mạn thuần tình của Ngựa Suối Nóng"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [],
    "match_mode": "contains",
    "basis": "Named theme song ゆこまロマン純情派 for the Yukoma Hot Springs scenario. The official Lantis release preserves the Japanese title and established international Uma Musume references romanize it as Yukoma Roman Junjoha; preserve that proper-name identity rather than a Vietnamese semantic calque.",
}

YUKOMA_ROMAN_JUNJOHA_DECISION = {
    "decision_id": "audit.finding.song-yukoma-roman-junjoha",
    "source_zh_cn": "汤驹浪漫纯情派",
    "action": "lock",
    "target_vi": "Yukoma Roman Junjoha",
    "kind": "proper_name",
    "category": "song",
    "note": "Verified song identity; use established Latin romanization Yukoma Roman Junjoha wherever the named title is referenced.",
}


def _load(path: Path, default: dict[str, Any] | None = None) -> dict[str, Any]:
    if not path.exists():
        return dict(default or {})
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def _upsert(items: list[Any], record: dict[str, Any], *, id_field: str) -> None:
    record_id = str(record[id_field])
    for index, item in enumerate(items):
        if isinstance(item, dict) and str(item.get(id_field) or "") == record_id:
            merged = dict(item)
            merged.update(record)
            items[index] = merged
            return
    items.append(dict(record))


def harden(repo_root: Path = ROOT) -> bool:
    changed = False
    community_path = repo_root / "glossary" / "ui_community_terms.json"
    community = _load(community_path, {"schema_version": 1, "terms": []})
    terms = community.setdefault("terms", [])
    if not isinstance(terms, list):
        raise ValueError("glossary/ui_community_terms.json terms must be a list")
    before = json.dumps(community, ensure_ascii=False, sort_keys=True)
    _upsert(terms, YUKOMA_ROMAN_JUNJOHA, id_field="id")
    if before != json.dumps(community, ensure_ascii=False, sort_keys=True):
        _write(community_path, community)
        changed = True

    reviews_path = repo_root / "glossary" / "terminology_reviews.json"
    reviews = _load(reviews_path, {"schema_version": 1, "decisions": []})
    decisions = reviews.setdefault("decisions", [])
    if not isinstance(decisions, list):
        raise ValueError("glossary/terminology_reviews.json decisions must be a list")
    before = json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    _upsert(decisions, YUKOMA_ROMAN_JUNJOHA_DECISION, id_field="decision_id")
    if before != json.dumps(reviews, ensure_ascii=False, sort_keys=True):
        _write(reviews_path, reviews)
        changed = True
    return changed


def main() -> int:
    changed = harden(ROOT)
    print(f"yukoma_roman_junjoha_song_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

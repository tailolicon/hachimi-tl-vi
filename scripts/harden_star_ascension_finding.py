from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

STAR_ASCENSION = {
    "id": "system.star_ascension.character_piece_description",
    "category": "progression",
    "source_aliases": ["才能开花"],
    "preferred": "Star Ascension",
    "compact": [],
    "accepted": ["Star Ascension"],
    "forbidden": ["Nở rộ tài năng", "Khai hoa tài năng"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [["114"]],
    "match_mode": "contains",
    "basis": "Named trainee progression mechanic. JP 才能開花 consumes Character Pieces to raise a trainee's star rarity; released Global player-facing terminology uses Star Ascension. Scope is restricted to text_data category 114 Character Piece descriptions so the separate Skill title 开花 and generic bloom/talent prose are unaffected.",
}

STAR_ASCENSION_DECISION = {
    "decision_id": "audit.finding.system-star-ascension",
    "source_zh_cn": "才能开花",
    "action": "lock",
    "target_vi": "Star Ascension",
    "kind": "system_label",
    "category": "progression",
    "note": "JP 才能開花 is the Character Piece star-rarity progression mechanic; preserve released Global player-facing label Star Ascension in category-114 Character Piece descriptions.",
}


def _load(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return dict(default)
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def _upsert(items: list[Any], record: dict[str, Any], id_field: str) -> None:
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
    before = json.dumps(community, ensure_ascii=False, sort_keys=True)
    _upsert(community.setdefault("terms", []), STAR_ASCENSION, "id")
    if before != json.dumps(community, ensure_ascii=False, sort_keys=True):
        _write(community_path, community)
        changed = True

    reviews_path = repo_root / "glossary" / "terminology_reviews.json"
    reviews = _load(reviews_path, {"schema_version": 1, "decisions": []})
    before = json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    _upsert(reviews.setdefault("decisions", []), STAR_ASCENSION_DECISION, "decision_id")
    if before != json.dumps(reviews, ensure_ascii=False, sort_keys=True):
        _write(reviews_path, reviews)
        changed = True
    return changed


def main() -> int:
    changed = harden(ROOT)
    print(f"star_ascension_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

"""Resolve repeated 菜月 NPC findings without inventing a reusable reading."""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "菜月(NPC)"

DECISION = {
    "decision_id": "audit.finding.npc-natsuki-unverified-reading",
    "source_zh_cn": SOURCE,
    "action": "ignore",
    "kind": "proper_name",
    "category": "proper_name",
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [
        ["152", "10"],
        ["152", "44"],
        ["152", "78"],
        ["152", "112"],
        ["152", "146"],
        ["152", "180"],
    ],
    "match_mode": "exact",
    "note": (
        "菜月 is a Japanese given-name spelling whose intended reading is not established by authoritative "
        "repository evidence. Existing localized data uses Natsuki, but that alone is not sufficient to promote "
        "a reusable canonical proper-name mapping. The source identity occurs at six repeated category-152 NPC "
        "items (10, 44, 78, 112, 146, 180). Ignore the canonical blocker only for those exact items and leave "
        "their displayed rendering to ordinary translation review."
    ),
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
    reviews_path = repo_root / "glossary" / "terminology_reviews.json"
    reviews = _load(reviews_path, {"schema_version": 1, "decisions": []})
    decisions = reviews.setdefault("decisions", [])
    if not isinstance(decisions, list):
        raise ValueError("glossary/terminology_reviews.json decisions must be a list")

    before = json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    _upsert(decisions, DECISION, id_field="decision_id")
    after = json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    if before == after:
        return False
    _write(reviews_path, reviews)
    return True


def main() -> int:
    changed = harden(ROOT)
    print(f"natsuki_npc_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

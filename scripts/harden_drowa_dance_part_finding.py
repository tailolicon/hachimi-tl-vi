from __future__ import annotations

"""Resolve one-off Drowa dance-part findings without inventing Latin titles."""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "ドロワダンスパート"
YEAR_SOURCE = "ドロワダンスパート2024"

DECISION = {
    "decision_id": "audit.finding.drowa-dance-part-unverified-title",
    "source_zh_cn": SOURCE,
    "action": "ignore",
    "kind": "proper_name",
    "category": "proper_name",
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [["16", "1080"]],
    "match_mode": "exact",
    "note": (
        "This is a one-off named track/event-part title. Repository research found no sufficiently "
        "authoritative official/catalog Latin rendering for the complete Japanese string. Do not "
        "invent Drowa Dance Part (or a year-suffixed variant) as reusable canonical terminology; "
        "leave the item to ordinary translation review instead of keeping a project-wide blocker."
    ),
}

YEAR_DECISION = {
    "decision_id": "audit.finding.drowa-dance-part-2024-unverified-title",
    "source_zh_cn": YEAR_SOURCE,
    "action": "ignore",
    "kind": "proper_name",
    "category": "proper_name",
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [["16", "1091"]],
    "match_mode": "exact",
    "note": (
        "This year-suffixed one-off title is covered by the same repository research as the adjacent "
        "Drowa dance-part item: no sufficiently authoritative official/catalog Latin rendering was "
        "found. Do not promote a guessed Drowa Dance Part 2024 rendering to reusable canonical "
        "terminology; leave this exact item to ordinary translation review."
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
    _upsert(decisions, YEAR_DECISION, id_field="decision_id")
    after = json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    if before == after:
        return False
    _write(reviews_path, reviews)
    return True


def main() -> int:
    changed = harden(ROOT)
    print(f"drowa_dance_part_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

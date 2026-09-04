from __future__ import annotations

"""Canonicalize the historical JRA race-class label 1000万下."""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "1000万下"
TARGET = "Hạng dưới 10 triệu yên"
TERM_ID = "race.class.historical.1000man_below"
DECISION_ID = "audit.finding.historical-1000man-race-class"

TERM = {
    "id": TERM_ID,
    "category": "race",
    "source_aliases": [SOURCE],
    "preferred": TARGET,
    "compact": [],
    "accepted": [TARGET],
    "forbidden": ["Dưới 10 triệu"],
    "require_accepted": True,
    "invalidation_scope": "source_path",
    "source_paths": ["localize_dict.json"],
    "match_mode": "exact",
    "basis": (
        "1000万下 is the historical JRA earnings-based race-class label that was renamed to the "
        "modern 2-win class (2勝クラス). Preserve the historical label wherever this exact system "
        "label appears in localize_dict.json rather than modernizing it, and make the omitted yen "
        "unit explicit in Vietnamese."
    ),
}

DECISION = {
    "decision_id": DECISION_ID,
    "source_zh_cn": SOURCE,
    "action": "lock",
    "target_vi": TARGET,
    "kind": "system_label",
    "category": "race",
    "note": (
        "Historical JRA class label: 1000万下 is the former name of today's 2-win class. Translate the "
        "historical label as Hạng dưới 10 triệu yên; the old Dưới 10 triệu drops both class context and currency."
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
    changed = False

    terms_path = repo_root / "glossary" / "ui_community_terms.json"
    payload = _load(terms_path, {"schema_version": 1, "terms": []})
    terms = payload.setdefault("terms", [])
    if not isinstance(terms, list):
        raise ValueError("glossary/ui_community_terms.json terms must be a list")
    before = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    _upsert(terms, TERM, id_field="id")
    if before != json.dumps(payload, ensure_ascii=False, sort_keys=True):
        _write(terms_path, payload)
        changed = True

    reviews_path = repo_root / "glossary" / "terminology_reviews.json"
    reviews = _load(reviews_path, {"schema_version": 1, "decisions": []})
    decisions = reviews.setdefault("decisions", [])
    if not isinstance(decisions, list):
        raise ValueError("glossary/terminology_reviews.json decisions must be a list")
    before = json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    _upsert(decisions, DECISION, id_field="decision_id")
    if before != json.dumps(reviews, ensure_ascii=False, sort_keys=True):
        _write(reviews_path, reviews)
        changed = True

    return changed


def main() -> int:
    changed = harden(ROOT)
    print(f"historical_1000man_race_class_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

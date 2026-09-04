from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "脚色十分"
TARGET = "Fully Charged"
KEY = "Race9467001"
FINDING_ID = "cf-642f6b7fcbe6af58"

RULE = {
    "id": "race_state.fully_charged",
    "category": "race_state",
    "source_aliases": [SOURCE],
    "preferred": TARGET,
    "compact": [],
    "accepted": [TARGET],
    "forbidden": ["Dư lực dồi dào", "Đủ sức chân", "Đầy sức"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["localize_dict.json"],
    "key_exact": [KEY],
    "match_mode": "exact",
    "basis": "Named race mechanic/state 脚色十分 is exposed by the English/Global terminology as Fully Charged. Scope is pinned to Race9467001 so ordinary descriptive prose cannot inherit the mechanic label.",
}

DECISION = {
    "decision_id": "audit.finding.race-state-fully-charged",
    "source_zh_cn": SOURCE,
    "action": "lock",
    "target_vi": TARGET,
    "kind": "system_label",
    "category": "race_state",
    "invalidation_scope": "item",
    "source_paths": ["localize_dict.json"],
    "key_exact": [KEY],
    "match_mode": "exact",
    "note": "Preserve the Global mechanic name Fully Charged for 脚色十分 at Race9467001; exact key scope prevents semantic overreach.",
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
    _upsert(community.setdefault("terms", []), RULE, "id")
    if before != json.dumps(community, ensure_ascii=False, sort_keys=True):
        _write(community_path, community)
        changed = True

    reviews_path = repo_root / "glossary" / "terminology_reviews.json"
    reviews = _load(reviews_path, {"schema_version": 1, "decisions": []})
    before = json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    _upsert(reviews.setdefault("decisions", []), DECISION, "decision_id")
    if before != json.dumps(reviews, ensure_ascii=False, sort_keys=True):
        _write(reviews_path, reviews)
        changed = True
    return changed


def main() -> int:
    changed = harden(ROOT)
    print(f"fully_charged_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

RUSHED_RACE_STATE = {
    "id": "race_state.rushed.text131",
    "category": "race_state",
    "source_aliases": ["焦躁"],
    "preferred": "Rushed",
    "compact": [],
    "accepted": ["Rushed"],
    "forbidden": ["Nóng vội", "nóng vội", "焦躁"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [["131"]],
    "match_mode": "contains",
    "basis": "Named in-race state corresponding to JP 掛かり. The released Global client/player-facing terminology is Rushed. Scope is restricted to text_data category 131 race objectives so 焦躁 inside unrelated Condition names, Skill names, or ordinary emotional prose is not canonicalized as this race state.",
}

RUSHED_RACE_STATE_DECISION = {
    "decision_id": "audit.finding.race-state-rushed",
    "source_zh_cn": "焦躁",
    "action": "lock",
    "target_vi": "Rushed",
    "kind": "system_label",
    "category": "race_state",
    "note": "Use released Global race-state label Rushed for zh-CN 焦躁 when it denotes JP 掛かり in category-131 race objectives; do not apply this lock to unrelated 焦躁 compounds or prose.",
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
    _upsert(community.setdefault("terms", []), RUSHED_RACE_STATE, "id")
    if before != json.dumps(community, ensure_ascii=False, sort_keys=True):
        _write(community_path, community)
        changed = True

    reviews_path = repo_root / "glossary" / "terminology_reviews.json"
    reviews = _load(reviews_path, {"schema_version": 1, "decisions": []})
    before = json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    _upsert(reviews.setdefault("decisions", []), RUSHED_RACE_STATE_DECISION, "decision_id")
    if before != json.dumps(reviews, ensure_ascii=False, sort_keys=True):
        _write(reviews_path, reviews)
        changed = True

    return changed


def main() -> int:
    changed = harden(ROOT)
    print(f"rushed_race_state_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

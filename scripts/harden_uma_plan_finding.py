from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "马娘计划"
TARGET = "Uma Plan"
KEY = "Character608001"

UMA_PLAN_TERM = {
    "id": "system.uma_plan.subscription.character608001",
    "category": "system",
    "source_aliases": [SOURCE],
    "preferred": TARGET,
    "compact": [],
    "accepted": [TARGET],
    "forbidden": ["Gói Umamusume", "Gói Uma Musume", "Kế hoạch Umamusume"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["localize_dict.json"],
    "key_exact": [KEY],
    "match_mode": "contains",
    "basis": "Official Cygames JP service name is ウマプラン (Uma Plan), introduced as a monthly subscription on 2026-02-24. Scope is pinned to the proven Character608001 subscription UI item so generic plan/package prose cannot overmatch.",
}

UMA_PLAN_DECISION = {
    "decision_id": "audit.finding.system-uma-plan",
    "source_zh_cn": SOURCE,
    "action": "lock",
    "target_vi": TARGET,
    "kind": "system_label",
    "category": "system",
    "invalidation_scope": "item",
    "source_paths": ["localize_dict.json"],
    "key_exact": [KEY],
    "match_mode": "contains",
    "note": "Cygames officially brands the service as ウマプラン. Preserve the brand identity as Uma Plan; the zh-CN alias occurs inside a longer Character608001 sentence, so contains matching is required and remains item-scoped.",
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

    reviews_path = repo_root / "glossary" / "terminology_reviews.json"
    reviews = _load(reviews_path, {"schema_version": 1, "decisions": []})
    before = json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    _upsert(reviews.setdefault("decisions", []), UMA_PLAN_DECISION, "decision_id")
    if before != json.dumps(reviews, ensure_ascii=False, sort_keys=True):
        _write(reviews_path, reviews)
        changed = True

    community_path = repo_root / "glossary" / "ui_community_terms.json"
    community = _load(community_path, {"schema_version": 1, "terms": []})
    before = json.dumps(community, ensure_ascii=False, sort_keys=True)
    _upsert(community.setdefault("terms", []), UMA_PLAN_TERM, "id")
    if before != json.dumps(community, ensure_ascii=False, sort_keys=True):
        _write(community_path, community)
        changed = True

    return changed


def main() -> int:
    changed = harden(ROOT)
    print(f"uma_plan_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

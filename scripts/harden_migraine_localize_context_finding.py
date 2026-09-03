from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BASE_TERM_ID = "common.condition.migraine"
BRIDGE_TERM_ID = "common.condition.migraine.localize_context"
DECISION_ID = "audit.finding.condition-migraine-localize-context"
ALIAS = "偏头痛"

BRIDGE_TERM = {
    "id": BRIDGE_TERM_ID,
    "category": "condition",
    "source_aliases": [ALIAS],
    "preferred": "Migraine",
    "compact": [],
    "accepted": ["Migraine"],
    "forbidden": ["đau nửa đầu", "Đau nửa đầu"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["localize_dict.json"],
    "match_mode": "contains",
    "basis": "偏头痛 is the established named negative Condition Migraine. The canonical table term remains scoped to the condition-name table, while worker evidence shows the same Condition referenced unquoted in localize_dict.json system UI (由于偏头痛，无法使用育成商品). Bridge only that source file so ordinary narrative text in other sources does not inherit the named-Condition rule.",
}

REVIEW_DECISION = {
    "decision_id": DECISION_ID,
    "source_zh_cn": ALIAS,
    "action": "lock",
    "target_vi": "Migraine",
    "kind": "terminology",
    "category": "condition",
    "note": "Named gameplay Condition 偏头痛 uses the established Global name Migraine; localize_dict.json system references are covered without widening the condition-table rule globally.",
}


def _load(path: Path, default: dict[str, Any] | None = None) -> dict[str, Any]:
    if not path.exists():
        return dict(default or {})
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def harden(repo_root: Path = ROOT) -> bool:
    changed = False

    community_path = repo_root / "glossary" / "ui_community_terms.json"
    community = _load(community_path)
    terms = community.get("terms")
    if not isinstance(terms, list):
        raise ValueError("glossary/ui_community_terms.json terms must be a list")
    if not any(isinstance(item, dict) and item.get("id") == BASE_TERM_ID for item in terms):
        raise ValueError(f"missing canonical base term {BASE_TERM_ID}")

    before = json.dumps(community, ensure_ascii=False, sort_keys=True)
    for index, item in enumerate(terms):
        if not isinstance(item, dict) or item.get("id") != BRIDGE_TERM_ID:
            continue
        merged = dict(item)
        merged.update(BRIDGE_TERM)
        terms[index] = merged
        break
    else:
        terms.append(dict(BRIDGE_TERM))
    if before != json.dumps(community, ensure_ascii=False, sort_keys=True):
        _write(community_path, community)
        changed = True

    reviews_path = repo_root / "glossary" / "terminology_reviews.json"
    reviews = _load(reviews_path, {"schema_version": 1, "decisions": []})
    decisions = reviews.setdefault("decisions", [])
    if not isinstance(decisions, list):
        raise ValueError("glossary/terminology_reviews.json decisions must be a list")
    before = json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    for index, item in enumerate(decisions):
        if not isinstance(item, dict) or item.get("decision_id") != DECISION_ID:
            continue
        merged = dict(item)
        merged.update(REVIEW_DECISION)
        decisions[index] = merged
        break
    else:
        decisions.append(dict(REVIEW_DECISION))
    if before != json.dumps(reviews, ensure_ascii=False, sort_keys=True):
        _write(reviews_path, reviews)
        changed = True

    return changed


def main() -> int:
    changed = harden(ROOT)
    print(f"migraine_localize_context_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BASE_TERM_ID = "event.loh.main_stage"
BRIDGE_TERM_ID = "event.loh.main_stage.main_segment_alias"
DECISION_ID = "audit.finding.loh-main-stage-main-segment-alias"
ALIAS = "主赛段"

BRIDGE_TERM = {
    "id": BRIDGE_TERM_ID,
    "category": "stage",
    "source_aliases": [ALIAS],
    "preferred": "Main Stage",
    "compact": [],
    "accepted": ["Main Stage"],
    "forbidden": ["Giai đoạn chính"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["localize_dict.json"],
    "match_mode": "contains",
    "basis": "League of Heroes zh-CN alias 主赛段 names the Main Stage. Keep the existing Heroes-key rule unchanged and bridge this worker-reported alias only within localize_dict.json so unrelated prose cannot inherit the event-stage meaning.",
}

REVIEW_DECISION = {
    "decision_id": DECISION_ID,
    "source_zh_cn": ALIAS,
    "action": "lock",
    "target_vi": "Main Stage",
    "kind": "terminology",
    "category": "event",
    "note": "League of Heroes alias 主赛段 denotes the named Main Stage. The community bridge constrains matching to localize_dict.json.",
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
    print(f"loh_main_stage_alias_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

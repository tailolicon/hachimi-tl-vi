from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

GRAND_LIVE_MENTAL_TEXT = {
    "id": "scenario.grand_live.performance.mental.text_data",
    "category": "scenario",
    "source_aliases": ["心理值"],
    "preferred": "Mental",
    "compact": [],
    "accepted": ["Mental"],
    "forbidden": ["Tinh thần", "điểm Tinh thần"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [],
    "match_mode": "contains",
    "basis": "Grand Live performance uses five named performance categories. zh-CN 心理值 is the Mental category; scope this alias to text_data_dict.json, matching the live finding scope while leaving generic 心理 prose untouched.",
}

GRAND_LIVE_MENTAL_UI = {
    "id": "scenario.grand_live.performance.mental.ui",
    "category": "scenario",
    "source_aliases": ["心理值"],
    "preferred": "Mental",
    "compact": [],
    "accepted": ["Mental"],
    "forbidden": ["Tinh thần"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["localize_dict.json"],
    "key_exact": ["SingleModeScenarioLive0005"],
    "match_mode": "exact",
    "basis": "Grand Live performance UI slot SingleModeScenarioLive0005 is the Mental category. Keep this rule item-scoped rather than treating generic 心理 as a global gameplay term.",
}

GRAND_LIVE_MENTAL_DECISION = {
    "decision_id": "audit.finding.grand-live-mental",
    "source_zh_cn": "心理值",
    "action": "lock",
    "target_vi": "Mental",
    "kind": "system_label",
    "category": "scenario",
    "note": "Grand Live performance category 心理值 is Mental. Canonical matching is constrained by scenario.grand_live.performance.mental.* rules.",
}

OBSOLETE_TEXT_RULE_ID = "scenario.grand_live.performance.mental.text131"


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
    terms[:] = [
        item
        for item in terms
        if not (isinstance(item, dict) and str(item.get("id") or "") == OBSOLETE_TEXT_RULE_ID)
    ]
    _upsert(terms, GRAND_LIVE_MENTAL_TEXT, id_field="id")
    _upsert(terms, GRAND_LIVE_MENTAL_UI, id_field="id")
    if before != json.dumps(community, ensure_ascii=False, sort_keys=True):
        _write(community_path, community)
        changed = True

    reviews_path = repo_root / "glossary" / "terminology_reviews.json"
    reviews = _load(reviews_path, {"schema_version": 1, "decisions": []})
    decisions = reviews.setdefault("decisions", [])
    if not isinstance(decisions, list):
        raise ValueError("glossary/terminology_reviews.json decisions must be a list")
    before = json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    _upsert(decisions, GRAND_LIVE_MENTAL_DECISION, id_field="decision_id")
    if before != json.dumps(reviews, ensure_ascii=False, sort_keys=True):
        _write(reviews_path, reviews)
        changed = True

    return changed


def main() -> int:
    changed = harden(ROOT)
    print(f"grand_live_mental_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

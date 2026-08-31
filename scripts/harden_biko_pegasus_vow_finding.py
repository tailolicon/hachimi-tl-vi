from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

VOW_FAMILY = {
    "id": "condition.biko_pegasus.passionate_vow.family",
    "category": "condition",
    "source_aliases": ["热血誓言"],
    "preferred": "Passionate Vow",
    "compact": [],
    "accepted": ["Passionate Vow"],
    "forbidden": ["Lời thề nhiệt huyết"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [["142"]],
    "match_mode": "contains",
    "exclude_source_contains": [
        "不可动摇的热血誓言・短距离",
        "不可动摇的热血誓言・英里",
    ],
    "basis": "Biko Pegasus named Condition family. zh-CN 热血誓言 maps to JP 熱き誓い; JP event guides verify Sprint and Mile variants. The umbrella rule exists only to resolve the worker-reported family finding; full labels below carry exact player-facing targets, and Unyielding variants are excluded from the umbrella so they cannot be collapsed to Passionate Vow.",
}

VOW_TERMS = (
    {
        "id": "condition.biko_pegasus.passionate_vow.sprint",
        "category": "condition",
        "source_aliases": ["热血誓言・短距离"],
        "preferred": "Passionate Vow - Sprint",
        "compact": [],
        "accepted": ["Passionate Vow - Sprint"],
        "forbidden": ["Lời thề nhiệt huyết・Cự ly ngắn"],
        "require_accepted": True,
        "invalidation_scope": "item",
        "source_paths": ["text_data_dict.json"],
        "json_path_prefixes": [["142"]],
        "match_mode": "exact",
        "basis": "Verified against JP 熱き誓い・短距離. Sprint follows the repository's canonical Global distance-class vocabulary.",
    },
    {
        "id": "condition.biko_pegasus.unyielding_vow.sprint",
        "category": "condition",
        "source_aliases": ["不可动摇的热血誓言・短距离"],
        "preferred": "Unyielding Vow - Sprint",
        "compact": [],
        "accepted": ["Unyielding Vow - Sprint"],
        "forbidden": ["Lời thề nhiệt huyết không lay chuyển・Cự ly ngắn"],
        "require_accepted": True,
        "invalidation_scope": "item",
        "source_paths": ["text_data_dict.json"],
        "json_path_prefixes": [["142"]],
        "match_mode": "exact",
        "basis": "Verified against JP 揺るぎない誓い・短距離. Sprint follows the repository's canonical Global distance-class vocabulary.",
    },
    {
        "id": "condition.biko_pegasus.passionate_vow.mile",
        "category": "condition",
        "source_aliases": ["热血誓言・英里"],
        "preferred": "Passionate Vow - Mile",
        "compact": [],
        "accepted": ["Passionate Vow - Mile"],
        "forbidden": ["Lời thề nhiệt huyết・Mile"],
        "require_accepted": True,
        "invalidation_scope": "item",
        "source_paths": ["text_data_dict.json"],
        "json_path_prefixes": [["142"]],
        "match_mode": "exact",
        "basis": "Verified against JP 熱き誓い・マイル.",
    },
    {
        "id": "condition.biko_pegasus.unyielding_vow.mile",
        "category": "condition",
        "source_aliases": ["不可动摇的热血誓言・英里"],
        "preferred": "Unyielding Vow - Mile",
        "compact": [],
        "accepted": ["Unyielding Vow - Mile"],
        "forbidden": ["Lời thề nhiệt huyết không lay chuyển・Mile"],
        "require_accepted": True,
        "invalidation_scope": "item",
        "source_paths": ["text_data_dict.json"],
        "json_path_prefixes": [["142"]],
        "match_mode": "exact",
        "basis": "Verified against JP 揺るぎない誓い・マイル.",
    },
)

VOW_DECISION = {
    "decision_id": "audit.finding.condition-biko-pegasus-passionate-vow-family",
    "source_zh_cn": "热血誓言",
    "action": "lock",
    "target_vi": "Passionate Vow",
    "kind": "condition",
    "category": "condition",
    "note": "Verified family identity: 热血誓言 maps to JP 熱き誓い in Biko Pegasus's Career; full Sprint/Mile and Unyielding variants are separately exact-scoped.",
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
    terms = community.setdefault("terms", [])
    _upsert(terms, VOW_FAMILY, "id")
    for term in VOW_TERMS:
        _upsert(terms, term, "id")
    if before != json.dumps(community, ensure_ascii=False, sort_keys=True):
        _write(community_path, community)
        changed = True

    reviews_path = repo_root / "glossary" / "terminology_reviews.json"
    reviews = _load(reviews_path, {"schema_version": 1, "decisions": []})
    before = json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    _upsert(reviews.setdefault("decisions", []), VOW_DECISION, "decision_id")
    if before != json.dumps(reviews, ensure_ascii=False, sort_keys=True):
        _write(reviews_path, reviews)
        changed = True
    return changed


def main() -> int:
    changed = harden(ROOT)
    print(f"biko_pegasus_vow_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

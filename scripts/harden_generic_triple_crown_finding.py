from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

GENERIC_TRIPLE_CROWN = {
    "id": "race.crown.generic_triple_crown_profile",
    "category": "race",
    "source_aliases": ["三冠"],
    "preferred": "Triple Crown",
    "compact": [],
    "accepted": ["Triple Crown"],
    "forbidden": ["Tam Quan", "Tam quan"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [["144"]],
    "match_mode": "contains",
    "basis": "Category 144 profile/title prose uses 三冠 as the generic Triple Crown achievement label. Keep the rule category-scoped so it cannot overmatch established compound crowns such as 经典三冠, 春古马三冠, or 秋古马三冠 elsewhere.",
}

GENERIC_TRIPLE_CROWN_DECISION = {
    "decision_id": "audit.finding.generic-triple-crown-profile",
    "source_zh_cn": "三冠",
    "action": "lock",
    "target_vi": "Triple Crown",
    "kind": "system_label",
    "category": "race",
    "note": "Resolve cf-f1601c34df2912ee only in category 144 profile/title text; preserve narrower established compound Triple Crown terms outside this scope.",
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
    rid = str(record[id_field])
    for index, item in enumerate(items):
        if isinstance(item, dict) and str(item.get(id_field) or "") == rid:
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
    _upsert(terms, GENERIC_TRIPLE_CROWN, "id")
    if before != json.dumps(community, ensure_ascii=False, sort_keys=True):
        _write(community_path, community)
        changed = True

    reviews_path = repo_root / "glossary" / "terminology_reviews.json"
    reviews = _load(reviews_path, {"schema_version": 1, "decisions": []})
    decisions = reviews.setdefault("decisions", [])
    if not isinstance(decisions, list):
        raise ValueError("glossary/terminology_reviews.json decisions must be a list")
    before = json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    _upsert(decisions, GENERIC_TRIPLE_CROWN_DECISION, "decision_id")
    if before != json.dumps(reviews, ensure_ascii=False, sort_keys=True):
        _write(reviews_path, reviews)
        changed = True

    return changed


def main() -> int:
    changed = harden(ROOT)
    print(f"generic_triple_crown_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

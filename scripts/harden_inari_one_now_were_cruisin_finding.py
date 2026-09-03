from __future__ import annotations

"""Canonicalize Inari One's Skill 100341 across title and factor-description surfaces."""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FINDING_ID = "cf-0cc9beacf4d177a8"
SOURCE_ZH_TITLE = "疾走乎,疾走乎！"
SOURCE_ZH_FACTOR = "疾走乎 疾走乎！"
SOURCE_JA = "快走かな、快走かな！"
PREFERRED = "Now We're Cruisin'!"
TITLE_TERM_ID = "skill.inari_one.now_were_cruisin.title147"
FACTOR_TERM_ID = "skill.inari_one.now_were_cruisin.factor172"

TITLE_TERM = {
    "id": TITLE_TERM_ID,
    "category": "skill_name",
    "source_aliases": [SOURCE_ZH_TITLE],
    "preferred": PREFERRED,
    "compact": [],
    "accepted": [PREFERRED],
    "forbidden": ["Chạy đi, chạy đi!", "Chạy nhanh nào, chạy nhanh nào!"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [["147"]],
    "match_mode": "exact",
    "basis": (
        "Skill ID 100341 is Inari One's JP unique Skill 快走かな、快走かな！. Released Global/EN data for "
        "[Edomurasaki] Inari One uses 'Now We're Cruisin'!'. Keep this rule exact and category-147 scoped so "
        "the stylized zh-CN title cannot normalize unrelated prose."
    ),
}

FACTOR_TERM = {
    "id": FACTOR_TERM_ID,
    "category": "skill_name",
    "source_aliases": [SOURCE_ZH_FACTOR],
    "preferred": PREFERRED,
    "compact": [],
    "accepted": [PREFERRED],
    "forbidden": ["Chạy đi, chạy đi!", "Chạy nhanh nào, chạy nhanh nào!"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [["172"]],
    "match_mode": "contains",
    "basis": (
        "Category-172 inheritance/factor descriptions embed the same Inari One Skill 100341 title using the "
        "zh-CN bridge form 疾走乎 疾走乎！. Released Global/EN identity is 'Now We're Cruisin'!'. Scope is "
        "restricted to category 172 and item invalidation."
    ),
}

DECISION = {
    "decision_id": "audit.finding.skill-inari-one-now-were-cruisin",
    "source_zh_cn": SOURCE_ZH_FACTOR,
    "action": "lock",
    "target_vi": PREFERRED,
    "kind": "skill_name",
    "category": "skill_name",
    "ja": [SOURCE_JA],
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [["172"]],
    "match_mode": "contains",
    "note": (
        "Verified identity: Inari One unique Skill ID 100341, JP 快走かな、快走かな！, released Global/EN "
        "title 'Now We're Cruisin!'. The category-147 standalone title is covered by a separate exact rule."
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

    community_path = repo_root / "glossary" / "ui_community_terms.json"
    community = _load(community_path, {"schema_version": 1, "terms": []})
    terms = community.setdefault("terms", [])
    if not isinstance(terms, list):
        raise ValueError("glossary/ui_community_terms.json terms must be a list")
    before = json.dumps(community, ensure_ascii=False, sort_keys=True)
    _upsert(terms, TITLE_TERM, id_field="id")
    _upsert(terms, FACTOR_TERM, id_field="id")
    if before != json.dumps(community, ensure_ascii=False, sort_keys=True):
        _write(community_path, community)
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
    print(f"inari_one_now_were_cruisin_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

"""Canonicalize Sounds of Earth's Che Piacevole! unique Skill across title/factor surfaces."""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FINDING_ID = "cf-24e795c0befb0e4f"
SOURCE_ZH = "真是愉快！"
SOURCE_JA = "ケ・ピアチェーヴォレ！"
PREFERRED = "Che Piacevole!"
TITLE_TERM_ID = "skill.sounds_of_earth.che_piacevole.title147"
FACTOR_TERM_ID = "skill.sounds_of_earth.che_piacevole.factor172"

TITLE_TERM = {
    "id": TITLE_TERM_ID,
    "category": "skill_name",
    "source_aliases": [SOURCE_ZH],
    "preferred": PREFERRED,
    "compact": [],
    "accepted": [PREFERRED],
    "forbidden": ["Thật vui quá!"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [["147"]],
    "match_mode": "exact",
    "basis": (
        "Pinned repository output already identifies the standalone Skill title as Che Piacevole!. "
        "JP Skill identity is ケ・ピアチェーヴォレ！, Sounds of Earth's unique Skill. Keep the "
        "established Italian-title rendering rather than translating the semantic zh-CN bridge literally."
    ),
}

FACTOR_TERM = {
    "id": FACTOR_TERM_ID,
    "category": "skill_name",
    "source_aliases": [SOURCE_ZH],
    "preferred": PREFERRED,
    "compact": [],
    "accepted": [PREFERRED],
    "forbidden": ["Thật vui quá!"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [["172"]],
    "match_mode": "contains",
    "basis": (
        "Category-172 inheritance descriptions embed the same unique Skill using zh-CN 真是愉快！. "
        "The repository's category-147 translation already uses Che Piacevole!, matching JP "
        "ケ・ピアチェーヴォレ！ identity. Scope remains category 172 with item invalidation."
    ),
}

DECISION = {
    "decision_id": "audit.finding.skill-sounds-of-earth-che-piacevole",
    "source_zh_cn": SOURCE_ZH,
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
        "Resolve the historical defer by matching the factor alias to Sounds of Earth's JP unique Skill "
        "ケ・ピアチェーヴォレ！ and the repository-established title Che Piacevole!."
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
    print(f"sounds_of_earth_che_piacevole_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

"""Canonicalize Marvelous Sunday's 万彩☆マーベラス★世界 unique Skill from JP identity."""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FINDING_ID = "cf-1c047ac10a89e52a"
SOURCE_ZH = "万彩☆美丽★世界"
SOURCE_JA = "万彩☆マーベラス★世界"
PREFERRED = "Vạn Sắc☆Marvelous★World"
TERM_ID = "skill.marvelous_sunday.myriad_marvelous_world"

TERM = {
    "id": TERM_ID,
    "category": "skill_name",
    "source_aliases": [SOURCE_ZH],
    "preferred": PREFERRED,
    "compact": [],
    "accepted": [PREFERRED],
    "forbidden": ["Vạn sắc☆Thế giới★Tươi đẹp"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [["147"]],
    "match_mode": "exact",
    "basis": (
        "Verified JP Skill 100551 is 万彩☆マーベラス★世界, Marvelous Sunday's unique Skill. "
        "The zh-CN bridge 万彩☆美丽★世界 semantically replaces the character's stylized "
        "マーベラス/Marvelous wording with generic 美丽 and therefore must not be translated "
        "literally. Vạn Sắc☆Marvelous★World keeps the JP title's myriad-color image, preserves "
        "Marvelous as the character-specific keyword, and retains the ☆/★ title styling."
    ),
}

DECISION = {
    "decision_id": "audit.finding.skill-marvelous-sunday-myriad-world",
    "source_zh_cn": SOURCE_ZH,
    "action": "lock",
    "target_vi": PREFERRED,
    "kind": "skill_name",
    "category": "skill_name",
    "ja": [SOURCE_JA],
    "note": (
        "JP identity verification resolves the source-bridge defer: Skill 100551 is "
        "万彩☆マーベラス★世界. Preserve Marvelous and the stylized punctuation rather than "
        "carrying zh-CN 美丽 into Vietnamese."
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
    _upsert(terms, TERM, id_field="id")
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
    print(f"marvelous_world_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

"""Canonicalize Dream Journey (Christmas)'s 夢寐に見る銀世界 unique Skill."""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FINDING_ID = "cf-1900e9e9aa8bd7ec"
SOURCE_ZH = "梦寐中的银色世界"
SOURCE_JA = "夢寐に見る銀世界"
PREFERRED = "Cõi Bạc Trong Mộng"

DREAM_JOURNEY_SILVER_WORLD = {
    "id": "skill.dream_journey.silver_world_in_dreams",
    "category": "skill_name",
    "source_aliases": [SOURCE_ZH],
    "preferred": PREFERRED,
    "compact": [],
    "accepted": [PREFERRED],
    "forbidden": ["Thế giới bạc trong giấc mơ"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "match_mode": "contains",
    "basis": (
        "Repository inheritance keys 11190201-11190203 belong to Dream Journey's "
        "Christmas trainee and carry the zh-CN alias 梦寐中的银色世界. Independent JP "
        "skill references identify Skill 111191 / inherited 911191 as 夢寐に見る銀世界, "
        "the unique Skill of [雪白の夢路] Dream Journey. Use JP as the semantic guard. "
        "Cõi Bạc Trong Mộng keeps 夢寐に見る ('seen in dreams') and the poetic 銀世界 "
        "('silver world', a snow-white landscape) while avoiding the stiff historical "
        "calque Thế giới bạc trong giấc mơ."
    ),
}

DREAM_JOURNEY_SILVER_WORLD_DECISION = {
    "decision_id": "audit.finding.skill-dream-journey-silver-world-in-dreams",
    "source_zh_cn": SOURCE_ZH,
    "action": "lock",
    "target_vi": PREFERRED,
    "kind": "skill_name",
    "category": "skill_name",
    "ja": [SOURCE_JA],
    "note": (
        "Verified JP identity is Dream Journey (Christmas)'s unique Skill "
        "夢寐に見る銀世界 (Skill 111191; inherited 911191). Lock one polished Vietnamese "
        "title, Cõi Bạc Trong Mộng, for both the title and inheritance-factor prose."
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
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


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
    _upsert(terms, DREAM_JOURNEY_SILVER_WORLD, id_field="id")
    if before != json.dumps(community, ensure_ascii=False, sort_keys=True):
        _write(community_path, community)
        changed = True

    reviews_path = repo_root / "glossary" / "terminology_reviews.json"
    reviews = _load(reviews_path, {"schema_version": 1, "decisions": []})
    decisions = reviews.setdefault("decisions", [])
    if not isinstance(decisions, list):
        raise ValueError("glossary/terminology_reviews.json decisions must be a list")
    before = json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    _upsert(decisions, DREAM_JOURNEY_SILVER_WORLD_DECISION, id_field="decision_id")
    if before != json.dumps(reviews, ensure_ascii=False, sort_keys=True):
        _write(reviews_path, reviews)
        changed = True

    return changed


def main() -> int:
    changed = harden(ROOT)
    print(f"dream_journey_silver_world_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

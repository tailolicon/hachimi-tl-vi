from __future__ import annotations

from scripts.build_terminology_review_queue import build_queue


def candidate(kind: str, source: str, category: str = "47", index: str = "1") -> dict:
    return {
        "id": f"{kind}:{source}",
        "kind": kind,
        "source_text": source,
        "source_category": category,
        "source_index": index,
    }


def test_review_queue_prioritizes_conflicts_then_observed_promotions():
    generated = {
        "total": 4,
        "candidates": [
            candidate("skill_name", "弧线教授"),
            candidate("race_name", "日本德比", "32", "2"),
            candidate("scenario_name", "URA总决赛", "999", "3"),
            candidate("character_name", "黄金船", "6", "1007"),
        ],
    }
    observed = {
        "observed_count": 1,
        "conflict_count": 1,
        "terms": [
            {"id": "observed:1", "zh_cn": ["日本德比"], "target_vi": "Japan Derby"}
        ],
        "conflicts": [
            {
                "source_zh_cn": "弧线教授",
                "targets_vi": ["Giáo sư Đường cong", "Bậc thầy Đường cong"],
            }
        ],
    }
    registry = {"terms": []}
    characters = {
        "characters": {
            "1007": {"canonical": "Gold Ship", "zh_cn": ["黄金船"]}
        }
    }

    result = build_queue(generated, observed, registry, characters)
    actionable = result["review_queue"]
    assert actionable[0]["source_zh_cn"] == "弧线教授"
    assert actionable[0]["status"] == "conflict_review"
    assert actionable[1]["source_zh_cn"] == "日本德比"
    assert actionable[1]["status"] == "promotion_candidate"
    assert any(
        row["source_zh_cn"] == "黄金船"
        and row["status"] == "handled_by_character_registry"
        for row in result["all_candidates"]
    )


def test_locked_term_is_not_actionable_and_unknown_character_is_identity_review():
    generated = {
        "total": 2,
        "candidates": [
            candidate("skill_name", "技能"),
            candidate("character_name", "未知马娘", "6", "9999"),
        ],
    }
    registry = {
        "terms": [
            {
                "id": "skill.generic",
                "zh_cn": ["技能"],
                "target_vi": "Kỹ năng",
                "locked": True,
            }
        ]
    }

    result = build_queue(generated, {}, registry, {"characters": {}})
    assert result["review_queue"][0]["source_zh_cn"] == "未知马娘"
    assert result["review_queue"][0]["status"] == "character_identity_review"
    locked = next(row for row in result["all_candidates"] if row["source_zh_cn"] == "技能")
    assert locked["status"] == "canonical_locked"
    assert locked["canonical_target_vi"] == "Kỹ năng"

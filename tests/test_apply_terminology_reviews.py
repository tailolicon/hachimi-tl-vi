from __future__ import annotations

import pytest

from scripts.apply_terminology_reviews import apply_reviews


def base_registry() -> dict:
    return {
        "schema_version": 2,
        "terms": [
            {
                "id": "stat.speed",
                "category": "stat",
                "zh_cn": ["速度"],
                "ja": ["スピード"],
                "target_vi": "Tốc độ",
                "locked": True,
            }
        ],
    }


def test_explicit_lock_adds_reviewed_term_and_is_idempotent():
    reviews = {
        "decisions": [
            {
                "decision_id": "skill-curve-professor",
                "action": "lock",
                "kind": "skill_name",
                "source_zh_cn": "弧线教授",
                "target_vi": "Giáo sư Đường cong",
                "ja": ["弧線のプロフェッサー"],
            }
        ]
    }
    first, stats = apply_reviews(base_registry(), reviews)
    assert stats["locked_added"] == 1
    added = first["terms"][-1]
    assert added["locked"] is True
    assert added["zh_cn"] == ["弧线教授"]
    assert added["target_vi"] == "Giáo sư Đường cong"
    assert added["review"]["decision_id"] == "skill-curve-professor"
    assert added["id"].startswith("reviewed.skill_name.")

    second, second_stats = apply_reviews(first, reviews)
    assert second_stats["locked_added"] == 0
    assert second_stats["locked_existing"] == 1
    assert second == first


def test_conflicting_locked_alias_is_rejected():
    reviews = {
        "decisions": [
            {
                "decision_id": "bad-speed",
                "action": "lock",
                "kind": "stat",
                "source_zh_cn": "速度",
                "target_vi": "Vận tốc",
            }
        ]
    }
    with pytest.raises(ValueError, match="locked alias"):
        apply_reviews(base_registry(), reviews)


def test_defer_and_ignore_do_not_touch_registry():
    reviews = {
        "decisions": [
            {"decision_id": "d1", "action": "defer", "source_zh_cn": "未知术语"},
            {"decision_id": "d2", "action": "ignore", "source_zh_cn": "装饰文本"},
        ]
    }
    updated, stats = apply_reviews(base_registry(), reviews)
    assert updated == base_registry()
    assert stats["deferred"] == 1
    assert stats["ignored"] == 1


def test_duplicate_decision_ids_are_rejected():
    reviews = {
        "decisions": [
            {"decision_id": "same", "action": "defer", "source_zh_cn": "A"},
            {"decision_id": "same", "action": "ignore", "source_zh_cn": "B"},
        ]
    }
    with pytest.raises(ValueError, match="duplicate decision_id"):
        apply_reviews(base_registry(), reviews)


def test_disjoint_scoped_locked_aliases_are_allowed():
    registry = {
        "schema_version": 2,
        "terms": [
            {"id": "race.miyako", "category": "race_name", "zh_cn": ["京城锦标"], "target_vi": "Miyako Stakes", "locked": True, "source_paths": ["text_data_dict.json"], "json_path_prefixes": [["32", "3061"], ["33", "3061"]], "match_mode": "exact"},
            {"id": "race.keio", "category": "race_name", "zh_cn": ["京城锦标"], "target_vi": "Keio Hai Nisai Stakes", "locked": True, "source_paths": ["text_data_dict.json"], "json_path_prefixes": [["111", "134"]], "match_mode": "exact"},
        ],
    }
    updated, stats = apply_reviews(registry, {"decisions": []})
    assert updated == registry
    assert stats["decisions"] == 0


def test_overlapping_scoped_locked_aliases_still_conflict():
    registry = {
        "schema_version": 2,
        "terms": [
            {"id": "race.a", "category": "race_name", "zh_cn": ["冲突名"], "target_vi": "Race A", "locked": True, "source_paths": ["text_data_dict.json"], "json_path_prefixes": [["111"]]},
            {"id": "race.b", "category": "race_name", "zh_cn": ["冲突名"], "target_vi": "Race B", "locked": True, "source_paths": ["text_data_dict.json"], "json_path_prefixes": [["111", "134"]]},
        ],
    }
    with pytest.raises(ValueError, match="internally conflicting"):
        apply_reviews(registry, {"decisions": []})

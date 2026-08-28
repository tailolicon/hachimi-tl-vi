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


def test_explicit_defer_and_ignore_are_removed_from_actionable_queue():
    generated = {
        "total": 3,
        "candidates": [
            candidate("skill_name", "延后术语"),
            candidate("support_card_title", "装饰短语", "76", "2"),
            candidate("race_name", "待处理比赛", "32", "3"),
        ],
    }
    reviews = {
        "decisions": [
            {"decision_id": "defer-1", "action": "defer", "source_zh_cn": "延后术语"},
            {"decision_id": "ignore-1", "action": "ignore", "source_zh_cn": "装饰短语"},
        ]
    }

    result = build_queue(generated, {}, {"terms": []}, {"characters": {}}, reviews)
    actionable_sources = {row["source_zh_cn"] for row in result["review_queue"]}
    assert "延后术语" not in actionable_sources
    assert "装饰短语" not in actionable_sources
    assert "待处理比赛" in actionable_sources
    deferred = next(row for row in result["all_candidates"] if row["source_zh_cn"] == "延后术语")
    ignored = next(row for row in result["all_candidates"] if row["source_zh_cn"] == "装饰短语")
    assert deferred["status"] == "reviewed_deferred"
    assert ignored["status"] == "reviewed_ignored"
    assert result["summary"]["explicit_review_decisions"] == 2


def test_worker_canonical_finding_is_actionable_even_with_conflicting_locked_term():
    generated = {"total": 1, "candidates": [candidate("race_name", "相性")]}
    registry = {"terms": [{"id": "legacy.bad", "zh_cn": ["相性"], "target_vi": "Tương thích", "locked": True}]}
    findings = {"findings": [{"finding_id": "cf-affinity", "status": "open", "source_zh_cn": "相性", "match_mode": "exact", "source_paths": ["localize_dict.json"], "suggested_targets_vi": ["Affinity"], "canonical_resolution": None, "review_resolution": None, "evidence_count": 2}]}
    result = build_queue(generated, {}, registry, {"characters": {}}, {}, findings)
    row = result["review_queue"][0]
    assert row["status"] == "canonical_finding_review"
    assert row["canonical_findings"][0]["finding_id"] == "cf-affinity"


def test_explicit_lock_stays_high_priority_until_registry_application():
    generated = {"total": 1, "candidates": [candidate("skill_name", "弧线教授")]}
    reviews = {
        "decisions": [
            {
                "decision_id": "lock-curve",
                "action": "lock",
                "source_zh_cn": "弧线教授",
                "target_vi": "Giáo sư Đường cong",
            }
        ]
    }
    result = build_queue(generated, {}, {"terms": []}, {"characters": {}}, reviews)
    assert result["review_queue"][0]["status"] == "pending_lock_application"
    assert result["review_queue"][0]["review_decision"]["decision_id"] == "lock-curve"

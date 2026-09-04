from __future__ import annotations

from scripts.build_translation_review_plan import _batch_priority_key, _hard_violation_count


def test_hard_violation_batch_outranks_heuristic_only_batch() -> None:
    hard_items = [{"risk_flags": ["community_term_mismatch"]}]
    heuristic_items = [{"risk_flags": ["very_long_target", "cjk_in_target"]}]
    batches = [
        {
            "batch_id": "heuristic",
            "source_batches": [1],
            "risk_score": 999,
            "hard_violation_count": _hard_violation_count(heuristic_items),
        },
        {
            "batch_id": "hard",
            "source_batches": [15],
            "risk_score": 10,
            "hard_violation_count": _hard_violation_count(hard_items),
        },
    ]

    assert [item["batch_id"] for item in sorted(batches, key=_batch_priority_key)] == ["hard", "heuristic"]


def test_equal_hard_violation_count_prefers_earlier_source_batch() -> None:
    batches = [
        {"batch_id": "later", "source_batches": [300], "risk_score": 100, "hard_violation_count": 1},
        {"batch_id": "earlier", "source_batches": [15], "risk_score": 10, "hard_violation_count": 1},
    ]

    assert [item["batch_id"] for item in sorted(batches, key=_batch_priority_key)] == ["earlier", "later"]


def test_multiple_hard_violations_outrank_single_violation() -> None:
    batches = [
        {"batch_id": "single", "source_batches": [1], "risk_score": 1000, "hard_violation_count": 1},
        {"batch_id": "multiple", "source_batches": [500], "risk_score": 1, "hard_violation_count": 2},
    ]

    assert [item["batch_id"] for item in sorted(batches, key=_batch_priority_key)] == ["multiple", "single"]

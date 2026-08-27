from scripts.merge_translation_review import _validate_result
from scripts.translation_review_common import (
    community_term_matches,
    locked_term_matches,
    suppress_overridden_locked_terms,
    text_fingerprint,
)


def _community_terms():
    return [
        {
            "id": "common.stat.stamina",
            "source_aliases": ["耐力"],
            "preferred": "Stamina",
            "accepted": ["Stamina"],
            "compact": [],
            "forbidden": ["Thể lực"],
            "require_accepted": True,
            "basis": "player-facing term",
        }
    ]


def _locked_terms():
    return [
        {
            "id": "stat.stamina",
            "zh_cn": ["耐力"],
            "target_vi": "Thể lực",
            "locked": True,
        }
    ]


def test_community_term_suppresses_conflicting_legacy_locked_mapping():
    source = "耐力上限提升"
    current = "Tăng giới hạn Thể lực"
    community = community_term_matches(None, source, current, _community_terms())
    locked = locked_term_matches(source, current, _locked_terms())

    filtered = suppress_overridden_locked_terms(locked, community)

    assert filtered == []
    assert community[0]["accepted_present"] is False
    assert community[0]["forbidden_present"] is True


def _batch_item():
    current = "Tăng giới hạn Thể lực"
    return {
        "uid": "zhcn:test-stamina",
        "source_text": "耐力上限提升",
        "source_fingerprint": "source-fp",
        "source_path": "localize_dict.json",
        "json_path": ["TestKey"],
        "current_text": current,
        "current_fingerprint": text_fingerprint(current),
        "locked_terms": [],
        "community_terms": [
            {
                "id": "common.stat.stamina",
                "accepted": ["Stamina"],
                "forbidden": ["Thể lực"],
                "require_accepted": True,
            }
        ],
        "skill_name_canonical": None,
    }


def _completion():
    return {
        "plan_id": "tr-p2-test",
        "batch_id": "tr-p2-test-b0001",
        "claim_id": "claim-1",
        "worker_id": "ChatGPT",
    }


def test_validator_rejects_keep_with_forbidden_player_term():
    item = _batch_item()
    completion = _completion()
    result = {
        **completion,
        "decisions": [
            {
                "uid": item["uid"],
                "current_fingerprint": item["current_fingerprint"],
                "action": "keep",
                "reason": "looks readable",
                "terminology_basis": "ui_community_terms:common.stat.stamina",
                "confidence": "high",
            }
        ],
    }

    _, errors = _validate_result(completion, result, {"items": [item]})

    assert any("forbidden wording" in error for error in errors)
    assert any("accepted player-facing form required" in error for error in errors)


def test_validator_accepts_revision_to_player_facing_term():
    item = _batch_item()
    completion = _completion()
    result = {
        **completion,
        "decisions": [
            {
                "uid": item["uid"],
                "current_fingerprint": item["current_fingerprint"],
                "action": "revise",
                "proposed_text": "Tăng giới hạn Stamina",
                "reason": "Use the accepted player-facing stat name.",
                "terminology_basis": "ui_community_terms:common.stat.stamina",
                "confidence": "high",
            }
        ],
    }

    _, errors = _validate_result(completion, result, {"items": [item]})

    assert errors == []


def test_defer_is_allowed_without_forcing_a_guess():
    item = _batch_item()
    completion = _completion()
    result = {
        **completion,
        "decisions": [
            {
                "uid": item["uid"],
                "current_fingerprint": item["current_fingerprint"],
                "action": "defer",
                "reason": "Need stronger context before changing this line.",
                "confidence": "low",
            }
        ],
    }

    decisions, errors = _validate_result(completion, result, {"items": [item]})

    assert errors == []
    assert decisions[0]["action"] == "defer"

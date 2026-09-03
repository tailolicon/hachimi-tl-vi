from scripts.merge_translation_review import _load_result, _validate_result
import json
from pathlib import Path

import pytest
from scripts.canonical_findings import active_findings
from scripts.translation_review_common import (
    community_term_matches,
    context_snapshot_hash,
    item_scoped_context_hash,
    item_scoped_policy_hash,
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


def test_missing_review_result_raises_batch_scoped_quarantinable_error(tmp_path):
    batch_id = "tr-p3-test-b0001"
    expected_result = Path("work/translation_review/results") / batch_id / "claim-missing.json"

    with pytest.raises(ValueError, match=rf"^{batch_id}: result file missing:"):
        _load_result(tmp_path, expected_result, batch_id)


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


def test_named_condition_exact_context_does_not_match_ordinary_prose():
    terms = [{
        "id": "common.condition.night_owl",
        "source_aliases": ["熬夜"],
        "preferred": "Night Owl",
        "accepted": ["Night Owl"],
        "forbidden": ["Thức khuya"],
        "require_accepted": True,
        "source_paths": ["text_data_dict.json"],
        "json_path_prefixes": [["142"]],
        "match_mode": "exact",
        "invalidation_scope": "item",
    }]
    matched = community_term_matches(
        None,
        "熬夜",
        "Thức khuya",
        terms,
        source_path="text_data_dict.json",
        json_path=["142", "1"],
    )
    assert matched and matched[0]["preferred"] == "Night Owl"
    assert community_term_matches(
        None,
        "总是会不自觉地熬夜",
        "Luôn vô thức thức khuya",
        terms,
        source_path="text_data_dict.json",
        json_path=["143", "1"],
    ) == []


def test_mood_level_requires_exact_ui_key():
    terms = [{
        "id": "common.state.mood.normal",
        "source_aliases": ["普通"],
        "preferred": "Normal",
        "accepted": ["Normal"],
        "forbidden": ["Bình thường"],
        "require_accepted": True,
        "source_paths": ["localize_dict.json"],
        "key_exact": ["Race0632"],
        "match_mode": "exact",
        "invalidation_scope": "item",
    }]
    assert community_term_matches(
        "Race0632", "普通", "Bình thường", terms,
        source_path="localize_dict.json", json_path=["Race0632"],
    )
    assert community_term_matches(
        "Menu999", "普通", "Bình thường", terms,
        source_path="localize_dict.json", json_path=["Menu999"],
    ) == []


def test_item_scoped_canon_changes_policy_hash_without_global_context_hash(tmp_path):
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    (tmp_path / "TRANSLATION_REVIEW.md").write_text("review", encoding="utf-8")
    (tmp_path / "GAME_CONTEXT.md").write_text("context", encoding="utf-8")
    for name in ("translation_audit_policy.json", "skill_name_style.json", "style_rules.json"):
        (glossary / name).write_text("{}", encoding="utf-8")
    (glossary / "term_registry.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "ui_community_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    global_before = context_snapshot_hash(tmp_path)
    scoped_before = item_scoped_policy_hash(tmp_path)
    scoped = {
        "id": "common.condition.night_owl",
        "source_aliases": ["熬夜"],
        "preferred": "Night Owl",
        "accepted": ["Night Owl"],
        "invalidation_scope": "item",
        "source_paths": ["text_data_dict.json"],
        "json_path_prefixes": [["142"]],
        "match_mode": "exact",
    }
    (glossary / "ui_community_terms.json").write_text(json.dumps({"terms": [scoped]}), encoding="utf-8")
    assert context_snapshot_hash(tmp_path) == global_before
    assert item_scoped_policy_hash(tmp_path) != scoped_before
    assert item_scoped_context_hash(
        key=None,
        source="熬夜",
        source_path="text_data_dict.json",
        json_path=["142", "1"],
        locked_terms=[],
        community_terms=[scoped],
    ) is not None
    assert item_scoped_context_hash(
        key=None,
        source="今天熬夜了",
        source_path="text_data_dict.json",
        json_path=["143", "1"],
        locked_terms=[],
        community_terms=[scoped],
    ) is None


def test_corner_adept_skill_family_matches_reviewed_canonical_lock():
    repo_root = Path(__file__).resolve().parents[1]
    payload = json.loads((repo_root / "glossary" / "skill_name_style.json").read_text(encoding="utf-8"))
    examples = {
        item["source_zh_cn"]: item["target_vi"]
        for item in payload.get("canonical_examples", [])
        if isinstance(item, dict) and item.get("source_zh_cn") and item.get("target_vi")
    }
    assert examples["弯道巧者○"] == "Thành thạo khúc cua○"
    assert examples["弯道巧者×"] == "Thành thạo khúc cua×"


def test_resolved_context_guard_finding_is_not_an_active_review_blocker():
    base = {
        "finding_id": "cf-power",
        "status": "open",
        "source_zh_cn": "力量",
        "match_mode": "contains",
        "source_paths": ["text_data_dict.json"],
        "key_exact": [],
        "json_path_prefixes": [],
        "review_resolution": None,
    }
    unresolved = {**base, "canonical_resolution": None}
    resolved = {
        **base,
        "canonical_resolution": {
            "layer": "context_guard",
            "term_id": "common.stat.power",
            "target_vi": "Power",
        },
    }

    assert active_findings({"findings": [unresolved]}) == [unresolved]
    assert active_findings({"findings": [resolved]}) == []

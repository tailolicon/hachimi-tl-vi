from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import refresh_canonical_resolutions
from scripts.harden_uma_plan_finding import DECISION_ID, KEYS, UMA_PLAN_TERM, harden


def _seed(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    (glossary / "ui_community_terms.json").write_text(json.dumps({"schema_version": 1, "terms": []}), encoding="utf-8")
    (glossary / "terminology_reviews.json").write_text(json.dumps({"schema_version": 1, "decisions": []}), encoding="utf-8")
    (glossary / "term_registry.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "source_bridge_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")


def _finding(key: str) -> dict:
    return {
        "finding_id": f"cf-test-uma-plan-{key}",
        "status": "open",
        "source_zh_cn": "马娘计划",
        "match_mode": "contains",
        "source_paths": ["localize_dict.json"],
        "key_exact": [key],
        "json_path_prefixes": [],
        "suggested_targets_vi": [],
        "canonical_resolution": None,
        "review_resolution": None,
    }


def test_hardener_resolves_official_uma_plan_brand_for_all_proven_keys_and_is_idempotent(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    community = json.loads((tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8"))
    rule = next(item for item in community["terms"] if item["id"] == UMA_PLAN_TERM["id"])
    assert rule["preferred"] == "Uma Plan"
    assert rule["source_paths"] == ["localize_dict.json"]
    assert rule["key_exact"] == KEYS
    assert rule["match_mode"] == "contains"

    for key in KEYS:
        resolved = refresh_canonical_resolutions(
            tmp_path,
            {"schema_version": 1, "findings": [_finding(key)]},
        )["findings"][0]
        assert resolved["canonical_resolution"] == {
            "layer": "community",
            "term_id": "system.uma_plan.subscription",
            "target_vi": "Uma Plan",
        }


def test_hardener_migrates_existing_generated_review_lock_scope_before_apply(tmp_path: Path) -> None:
    _seed(tmp_path)
    registry_path = tmp_path / "glossary" / "term_registry.json"
    registry_path.write_text(
        json.dumps(
            {
                "terms": [
                    {
                        "id": "reviewed.system_label.514dfaebdb54",
                        "category": "system",
                        "zh_cn": ["马娘计划"],
                        "target_vi": "Uma Plan",
                        "locked": True,
                        "review": {
                            "decision_id": DECISION_ID,
                            "source": "glossary/terminology_reviews.json",
                        },
                        "invalidation_scope": "item",
                        "source_paths": ["localize_dict.json"],
                        "key_exact": ["Character608001"],
                        "match_mode": "contains",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    assert harden(tmp_path) is True
    assert harden(tmp_path) is False
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    lock = registry["terms"][0]
    assert lock["review"]["decision_id"] == DECISION_ID
    assert lock["key_exact"] == KEYS
    assert lock["source_paths"] == ["localize_dict.json"]
    assert lock["match_mode"] == "contains"


def test_rule_does_not_resolve_same_alias_outside_proven_subscription_keys(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    outside = refresh_canonical_resolutions(
        tmp_path,
        {"schema_version": 1, "findings": [_finding("UnrelatedPlan001")]},
    )["findings"][0]
    assert outside["canonical_resolution"] is None

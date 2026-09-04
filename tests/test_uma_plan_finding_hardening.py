from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import refresh_canonical_resolutions
from scripts.harden_uma_plan_finding import KEY, UMA_PLAN_TERM, harden


def _seed(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    (glossary / "ui_community_terms.json").write_text(json.dumps({"schema_version": 1, "terms": []}), encoding="utf-8")
    (glossary / "terminology_reviews.json").write_text(json.dumps({"schema_version": 1, "decisions": []}), encoding="utf-8")
    (glossary / "term_registry.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "source_bridge_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")


def _finding(key: str) -> dict:
    return {
        "finding_id": "cf-test-uma-plan",
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


def test_hardener_resolves_official_uma_plan_brand_and_is_idempotent(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    community = json.loads((tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8"))
    rule = next(item for item in community["terms"] if item["id"] == UMA_PLAN_TERM["id"])
    assert rule["preferred"] == "Uma Plan"
    assert rule["source_paths"] == ["localize_dict.json"]
    assert rule["key_exact"] == [KEY]
    assert rule["match_mode"] == "contains"

    resolved = refresh_canonical_resolutions(
        tmp_path,
        {"schema_version": 1, "findings": [_finding(KEY)]},
    )["findings"][0]
    assert resolved["canonical_resolution"] == {
        "layer": "community",
        "term_id": "system.uma_plan.subscription.character608001",
        "target_vi": "Uma Plan",
    }


def test_rule_does_not_resolve_same_alias_outside_proven_subscription_key(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    outside = refresh_canonical_resolutions(
        tmp_path,
        {"schema_version": 1, "findings": [_finding("UnrelatedPlan001")]},
    )["findings"][0]
    assert outside["canonical_resolution"] is None

from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import refresh_canonical_resolutions
from scripts.harden_team_building_scout_finding import (
    TEAM_BUILDING_SCOUT,
    TEAM_BUILDING_SCOUT_POINTS,
    harden,
)


def _seed(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    (glossary / "ui_community_terms.json").write_text(json.dumps({"schema_version": 1, "terms": []}), encoding="utf-8")
    (glossary / "terminology_reviews.json").write_text(json.dumps({"schema_version": 1, "decisions": []}), encoding="utf-8")
    (glossary / "term_registry.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "source_bridge_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")


def _finding(*, key: str) -> dict:
    return {
        "finding_id": "cf-test-team-building-scout",
        "status": "open",
        "source_zh_cn": "签约",
        "match_mode": "contains",
        "source_paths": ["localize_dict.json"],
        "key_exact": [key],
        "json_path_prefixes": [],
        "suggested_targets_vi": [],
        "canonical_resolution": None,
        "review_resolution": None,
    }


def test_hardener_resolves_team_building_scout_and_is_idempotent(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    community = json.loads((tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8"))
    scout = next(item for item in community["terms"] if item["id"] == TEAM_BUILDING_SCOUT["id"])
    points = next(item for item in community["terms"] if item["id"] == TEAM_BUILDING_SCOUT_POINTS["id"])
    assert scout["preferred"] == "Scout"
    assert scout["source_paths"] == ["localize_dict.json"]
    assert "TeamBuilding020022" in scout["key_exact"]
    assert points["preferred"] == "Scout Points"
    assert points["key_exact"] == ["TeamBuilding020023", "TeamBuilding020025"]

    ledger = {"schema_version": 1, "findings": [_finding(key="TeamBuilding020022")]}
    finding = refresh_canonical_resolutions(tmp_path, ledger)["findings"][0]
    assert finding["review_resolution"]["target_vi"] == "Scout"
    assert finding["canonical_resolution"] == {
        "layer": "community",
        "term_id": "event.aim_for_the_stars.scout",
        "target_vi": "Scout",
    }


def test_rule_does_not_resolve_same_alias_outside_team_building_keys(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    ledger = {"schema_version": 1, "findings": [_finding(key="UnrelatedContract001")]}
    finding = refresh_canonical_resolutions(tmp_path, ledger)["findings"][0]
    assert finding["canonical_resolution"] is None

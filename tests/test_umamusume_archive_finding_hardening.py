from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import refresh_canonical_resolutions
from scripts.harden_umamusume_archive_finding import UMAMUSUME_ARCHIVE_TEAM_BUILDING, harden


def _seed(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    (glossary / "ui_community_terms.json").write_text(json.dumps({"schema_version": 1, "terms": []}), encoding="utf-8")
    (glossary / "terminology_reviews.json").write_text(json.dumps({"schema_version": 1, "decisions": []}), encoding="utf-8")
    (glossary / "term_registry.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "source_bridge_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")


def _finding(key: str) -> dict:
    return {
        "finding_id": "cf-test-umamusume-archive",
        "status": "open",
        "source_zh_cn": "赛马娘名鉴",
        "match_mode": "contains",
        "source_paths": ["localize_dict.json"],
        "key_exact": [key],
        "json_path_prefixes": [],
        "suggested_targets_vi": [],
        "canonical_resolution": None,
        "review_resolution": None,
    }


def test_team_building_archive_resolves_and_is_idempotent(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    community = json.loads((tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8"))
    rule = next(item for item in community["terms"] if item["id"] == UMAMUSUME_ARCHIVE_TEAM_BUILDING["id"])
    assert rule["preferred"] == "Archive"
    assert rule["key_exact"] == ["TeamBuilding619002"]

    resolved = refresh_canonical_resolutions(
        tmp_path,
        {"schema_version": 1, "findings": [_finding("TeamBuilding619002")]},
    )["findings"][0]
    assert resolved["review_resolution"]["target_vi"] == "Archive"
    assert resolved["canonical_resolution"] == {
        "layer": "community",
        "term_id": "system.archive.team_building_619002",
        "target_vi": "Archive",
    }


def test_archive_rule_does_not_escape_proven_team_building_key(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    resolved = refresh_canonical_resolutions(
        tmp_path,
        {"schema_version": 1, "findings": [_finding("UnrelatedArchive001")]},
    )["findings"][0]
    assert resolved["canonical_resolution"] is None

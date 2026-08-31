from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import refresh_canonical_resolutions
from scripts.harden_casino_drive_finding import CASINO_DRIVE, CASINO_DRIVE_DECISION, harden


def _seed(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    (glossary / "ui_community_terms.json").write_text(json.dumps({"schema_version": 1, "terms": []}), encoding="utf-8")
    (glossary / "terminology_reviews.json").write_text(json.dumps({"schema_version": 1, "decisions": []}), encoding="utf-8")
    (glossary / "term_registry.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "source_bridge_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")


def _finding(prefix: str) -> dict:
    return {
        "finding_id": "cf-096e09d8c05dcc89",
        "status": "open",
        "source_zh_cn": "夺金旅途",
        "match_mode": "contains",
        "source_paths": ["text_data_dict.json"],
        "key_exact": [],
        "json_path_prefixes": [[prefix]],
        "suggested_targets_vi": [],
        "canonical_resolution": None,
        "review_resolution": None,
    }


def test_hardener_resolves_casino_drive_scenario_and_is_idempotent(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    community = json.loads((tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8"))
    rule = next(item for item in community["terms"] if item["id"] == CASINO_DRIVE["id"])
    assert rule["preferred"] == "Casino Drive"
    assert rule["json_path_prefixes"] == [["120"]]
    assert "Stay Gold" in rule["forbidden"]

    reviews = json.loads((tmp_path / "glossary" / "terminology_reviews.json").read_text(encoding="utf-8"))
    decision = next(item for item in reviews["decisions"] if item["decision_id"] == CASINO_DRIVE_DECISION["decision_id"])
    assert decision["target_vi"] == "Casino Drive"

    finding = refresh_canonical_resolutions(tmp_path, {"schema_version": 1, "findings": [_finding("120")]})["findings"][0]
    assert finding["canonical_resolution"] == {
        "layer": "community",
        "term_id": "proper_name.casino_drive.scenario120",
        "target_vi": "Casino Drive",
    }


def test_rule_does_not_resolve_same_alias_outside_scenario_category(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    finding = refresh_canonical_resolutions(tmp_path, {"schema_version": 1, "findings": [_finding("147")]})["findings"][0]
    assert finding["canonical_resolution"] is None

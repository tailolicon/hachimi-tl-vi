from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import refresh_canonical_resolutions
from scripts.harden_rushed_race_state_finding import RUSHED_RACE_STATE, harden


def _seed(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    (glossary / "ui_community_terms.json").write_text(json.dumps({"schema_version": 1, "terms": []}), encoding="utf-8")
    (glossary / "terminology_reviews.json").write_text(json.dumps({"schema_version": 1, "decisions": []}), encoding="utf-8")
    (glossary / "term_registry.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "source_bridge_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")


def _finding(prefix: str) -> dict:
    return {
        "finding_id": "cf-test-rushed-race-state",
        "status": "open",
        "source_zh_cn": "焦躁",
        "match_mode": "contains",
        "source_paths": ["text_data_dict.json"],
        "key_exact": [],
        "json_path_prefixes": [[prefix]],
        "suggested_targets_vi": [],
        "canonical_resolution": None,
        "review_resolution": None,
    }


def test_rushed_race_state_resolves_category_131_and_is_idempotent(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    community = json.loads((tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8"))
    rule = next(item for item in community["terms"] if item["id"] == RUSHED_RACE_STATE["id"])
    assert rule["preferred"] == "Rushed"
    assert rule["json_path_prefixes"] == [["131"]]
    assert rule["match_mode"] == "contains"

    resolved = refresh_canonical_resolutions(
        tmp_path,
        {"schema_version": 1, "findings": [_finding("131")]},
    )["findings"][0]
    assert resolved["review_resolution"]["target_vi"] == "Rushed"
    assert resolved["canonical_resolution"] == {
        "layer": "community",
        "term_id": "race_state.rushed.text131",
        "target_vi": "Rushed",
    }


def test_rushed_rule_does_not_escape_race_objective_category(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    resolved = refresh_canonical_resolutions(
        tmp_path,
        {"schema_version": 1, "findings": [_finding("142")]},
    )["findings"][0]
    assert resolved["canonical_resolution"] is None

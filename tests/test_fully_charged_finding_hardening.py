from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import refresh_canonical_resolutions
from scripts.harden_fully_charged_finding import DECISION, FINDING_ID, KEY, RULE, SOURCE, TARGET, harden


def _seed(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    (glossary / "ui_community_terms.json").write_text(json.dumps({"schema_version": 1, "terms": []}), encoding="utf-8")
    (glossary / "terminology_reviews.json").write_text(json.dumps({"schema_version": 1, "decisions": []}), encoding="utf-8")
    (glossary / "term_registry.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "source_bridge_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")


def _finding(key: str) -> dict:
    return {
        "finding_id": FINDING_ID,
        "status": "open",
        "source_zh_cn": SOURCE,
        "match_mode": "exact",
        "source_paths": ["localize_dict.json"],
        "key_exact": [key],
        "json_path_prefixes": [],
        "suggested_targets_vi": [],
        "canonical_resolution": None,
        "review_resolution": None,
    }


def test_fully_charged_resolves_exact_race_state_key(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    community = json.loads((tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8"))
    rule = next(item for item in community["terms"] if item["id"] == RULE["id"])
    assert rule["preferred"] == TARGET
    assert rule["key_exact"] == [KEY]
    assert rule["match_mode"] == "exact"

    reviews = json.loads((tmp_path / "glossary" / "terminology_reviews.json").read_text(encoding="utf-8"))
    decision = next(item for item in reviews["decisions"] if item["decision_id"] == DECISION["decision_id"])
    assert decision["target_vi"] == TARGET
    assert decision["key_exact"] == [KEY]

    resolved = refresh_canonical_resolutions(tmp_path, {"schema_version": 1, "findings": [_finding(KEY)]})["findings"][0]
    assert resolved["review_resolution"]["target_vi"] == TARGET
    assert resolved["canonical_resolution"] == {
        "layer": "community",
        "term_id": RULE["id"],
        "target_vi": TARGET,
    }


def test_fully_charged_does_not_resolve_other_localize_key(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    resolved = refresh_canonical_resolutions(tmp_path, {"schema_version": 1, "findings": [_finding("Race9467002")]})["findings"][0]
    assert resolved["canonical_resolution"] is None

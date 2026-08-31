from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import refresh_canonical_resolutions
from scripts.harden_mood_great_text_data_finding import MOOD_GREAT_TEXT_DATA, MOOD_GREAT_TEXT_DATA_DECISION, harden


def _seed(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    (glossary / "ui_community_terms.json").write_text(json.dumps({"schema_version": 1, "terms": []}), encoding="utf-8")
    (glossary / "terminology_reviews.json").write_text(json.dumps({"schema_version": 1, "decisions": []}), encoding="utf-8")
    (glossary / "term_registry.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "source_bridge_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")


def _finding(source: str = "绝好调") -> dict:
    return {
        "finding_id": "cf-4f93e36d34c69cf9",
        "status": "open",
        "source_zh_cn": source,
        "match_mode": "contains",
        "source_paths": ["text_data_dict.json"],
        "key_exact": [],
        "json_path_prefixes": [],
        "suggested_targets_vi": ["Great"],
        "canonical_resolution": None,
        "review_resolution": None,
    }


def test_hardener_resolves_great_mood_and_is_idempotent(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    community = json.loads((tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8"))
    rule = next(item for item in community["terms"] if item["id"] == MOOD_GREAT_TEXT_DATA["id"])
    assert rule["preferred"] == "Great"
    assert rule["source_aliases"] == ["绝好调"]
    assert rule["source_paths"] == ["text_data_dict.json"]

    reviews = json.loads((tmp_path / "glossary" / "terminology_reviews.json").read_text(encoding="utf-8"))
    decision = next(item for item in reviews["decisions"] if item["decision_id"] == MOOD_GREAT_TEXT_DATA_DECISION["decision_id"])
    assert decision["target_vi"] == "Great"

    finding = refresh_canonical_resolutions(tmp_path, {"schema_version": 1, "findings": [_finding()]})["findings"][0]
    assert finding["canonical_resolution"] == {
        "layer": "community",
        "term_id": "state.mood.great.text_data",
        "target_vi": "Great",
    }


def test_rule_does_not_resolve_generic_good_condition_word(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    finding = refresh_canonical_resolutions(tmp_path, {"schema_version": 1, "findings": [_finding("好调")]})["findings"][0]
    assert finding["canonical_resolution"] is None

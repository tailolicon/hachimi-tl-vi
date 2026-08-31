from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import refresh_canonical_resolutions
from scripts.harden_graded_race_finding import GRADED_RACE, harden


def _seed(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    (glossary / "ui_community_terms.json").write_text(json.dumps({"schema_version": 1, "terms": []}), encoding="utf-8")
    (glossary / "terminology_reviews.json").write_text(json.dumps({"schema_version": 1, "decisions": []}), encoding="utf-8")
    (glossary / "term_registry.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "source_bridge_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")


def _finding(*, source_path: str = "text_data_dict.json") -> dict:
    return {
        "finding_id": "cf-bf5645acbcfad6a9",
        "status": "open",
        "source_zh_cn": "重赏",
        "match_mode": "contains",
        "source_paths": [source_path],
        "key_exact": [],
        "json_path_prefixes": [],
        "suggested_targets_vi": [],
        "canonical_resolution": None,
        "review_resolution": None,
    }


def test_hardener_resolves_graded_race_finding_and_is_idempotent(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    community = json.loads((tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8"))
    rule = next(item for item in community["terms"] if item["id"] == GRADED_RACE["id"])
    assert rule["preferred"] == "graded"
    assert rule["source_paths"] == ["text_data_dict.json"]
    assert rule["match_mode"] == "contains"
    assert "trọng thưởng" in rule["forbidden"]

    finding = refresh_canonical_resolutions(tmp_path, {"schema_version": 1, "findings": [_finding()]})["findings"][0]
    assert finding["review_resolution"]["target_vi"] == "graded"
    assert finding["canonical_resolution"] == {
        "layer": "community",
        "term_id": "race.graded",
        "target_vi": "graded",
    }


def test_rule_does_not_resolve_same_alias_outside_text_data(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    finding = refresh_canonical_resolutions(
        tmp_path,
        {"schema_version": 1, "findings": [_finding(source_path="localize_dict.json")]},
    )["findings"][0]
    assert finding["canonical_resolution"] is None

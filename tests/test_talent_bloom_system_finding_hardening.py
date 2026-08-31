from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import refresh_canonical_resolutions
from scripts.harden_talent_bloom_system_finding import harden


def _seed(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    (glossary / "ui_community_terms.json").write_text(json.dumps({"schema_version": 1, "terms": []}), encoding="utf-8")
    (glossary / "terminology_reviews.json").write_text(json.dumps({"schema_version": 1, "decisions": []}), encoding="utf-8")
    (glossary / "term_registry.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "source_bridge_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")


def _finding(source_path: str, prefixes: list[list[str]], *, mode: str = "contains") -> dict:
    return {
        "finding_id": "cf-test-talent-bloom",
        "status": "open",
        "source_zh_cn": "才能开花",
        "match_mode": mode,
        "source_paths": [source_path],
        "key_exact": [],
        "json_path_prefixes": prefixes,
        "suggested_targets_vi": [],
        "canonical_resolution": None,
        "review_resolution": None,
    }


def test_compatibility_hardener_migrates_category_114_and_localize_to_star_ascension(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    for finding in (
        _finding("text_data_dict.json", [["114"]]),
        _finding("localize_dict.json", [], mode="exact"),
    ):
        resolved = refresh_canonical_resolutions(tmp_path, {"schema_version": 1, "findings": [finding]})["findings"][0]
        assert resolved["review_resolution"]["target_vi"] == "Star Ascension"
        assert resolved["canonical_resolution"]["target_vi"] == "Star Ascension"
        assert resolved["canonical_resolution"]["layer"] == "community"


def test_text_rule_does_not_escape_category_114(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    resolved = refresh_canonical_resolutions(
        tmp_path,
        {"schema_version": 1, "findings": [_finding("text_data_dict.json", [["147"]])]},
    )["findings"][0]
    assert resolved["canonical_resolution"] is None


def test_localize_rule_requires_complete_phrase(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    partial = _finding("localize_dict.json", [], mode="contains")
    partial["source_zh_cn"] = "开花"
    resolved = refresh_canonical_resolutions(tmp_path, {"schema_version": 1, "findings": [partial]})["findings"][0]
    assert resolved["canonical_resolution"] is None

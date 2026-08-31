from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import refresh_canonical_resolutions
from scripts.harden_yukoma_roman_junjoha_song_finding import (
    YUKOMA_ROMAN_JUNJOHA,
    YUKOMA_ROMAN_JUNJOHA_DECISION,
    harden,
)


def _seed(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    (glossary / "ui_community_terms.json").write_text(json.dumps({"schema_version": 1, "terms": []}), encoding="utf-8")
    (glossary / "terminology_reviews.json").write_text(json.dumps({"schema_version": 1, "decisions": []}), encoding="utf-8")
    (glossary / "term_registry.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "source_bridge_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")


def test_yukoma_roman_junjoha_resolves_named_song_reference(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False
    community = json.loads((tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8"))
    rule = next(item for item in community["terms"] if item["id"] == YUKOMA_ROMAN_JUNJOHA["id"])
    assert rule["preferred"] == "Yukoma Roman Junjoha"
    assert rule["match_mode"] == "contains"
    reviews = json.loads((tmp_path / "glossary" / "terminology_reviews.json").read_text(encoding="utf-8"))
    decision = next(item for item in reviews["decisions"] if item["decision_id"] == YUKOMA_ROMAN_JUNJOHA_DECISION["decision_id"])
    assert decision["target_vi"] == "Yukoma Roman Junjoha"
    ledger = {"schema_version": 1, "findings": [{
        "finding_id": "cf-28cf7c0b1249e7f2", "status": "open", "source_zh_cn": "汤驹浪漫纯情派",
        "match_mode": "contains", "source_paths": ["text_data_dict.json"], "key_exact": [],
        "json_path_prefixes": [], "suggested_targets_vi": [],
        "canonical_resolution": None, "review_resolution": None,
    }]}
    finding = refresh_canonical_resolutions(tmp_path, ledger)["findings"][0]
    assert finding["review_resolution"]["target_vi"] == "Yukoma Roman Junjoha"
    assert finding["canonical_resolution"] == {
        "layer": "community", "term_id": "song.yukoma_roman_junjoha", "target_vi": "Yukoma Roman Junjoha"
    }


def test_yukoma_roman_junjoha_does_not_resolve_other_source_path(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    ledger = {"schema_version": 1, "findings": [{
        "finding_id": "cf-test-yukoma-wrong", "status": "open", "source_zh_cn": "汤驹浪漫纯情派",
        "match_mode": "contains", "source_paths": ["localize_dict.json"], "key_exact": [],
        "json_path_prefixes": [], "suggested_targets_vi": [],
        "canonical_resolution": None, "review_resolution": None,
    }]}
    assert refresh_canonical_resolutions(tmp_path, ledger)["findings"][0]["canonical_resolution"] is None

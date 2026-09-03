from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import refresh_canonical_resolutions
from scripts.harden_senior_autumn_triple_crown_finding import (
    SENIOR_AUTUMN_TRIPLE_CROWN,
    SENIOR_AUTUMN_TRIPLE_CROWN_DECISION,
    harden,
)


def _seed(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    (glossary / "ui_community_terms.json").write_text(json.dumps({"schema_version": 1, "terms": []}), encoding="utf-8")
    (glossary / "terminology_reviews.json").write_text(json.dumps({"schema_version": 1, "decisions": []}), encoding="utf-8")
    (glossary / "term_registry.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "source_bridge_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")


def _finding(source_path: str = "text_data_dict.json") -> dict:
    return {
        "finding_id": "cf-97dd9d6e5657d6f9",
        "status": "open",
        "source_zh_cn": "秋古马三冠",
        "match_mode": "contains",
        "source_paths": [source_path],
        "key_exact": [],
        "json_path_prefixes": [],
        "suggested_targets_vi": ["Senior Autumn Triple Crown"],
        "canonical_resolution": None,
        "review_resolution": None,
    }


def test_senior_autumn_triple_crown_resolves_live_finding_scope(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    community = json.loads((tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8"))
    term = next(item for item in community["terms"] if item["id"] == SENIOR_AUTUMN_TRIPLE_CROWN["id"])
    assert term["source_paths"] == ["text_data_dict.json"]
    assert term["match_mode"] == "contains"

    reviews = json.loads((tmp_path / "glossary" / "terminology_reviews.json").read_text(encoding="utf-8"))
    decision = next(item for item in reviews["decisions"] if item["decision_id"] == SENIOR_AUTUMN_TRIPLE_CROWN_DECISION["decision_id"])
    assert decision["target_vi"] == "Senior Autumn Triple Crown"

    finding = refresh_canonical_resolutions(
        tmp_path,
        {"schema_version": 1, "findings": [_finding()]},
    )["findings"][0]
    assert finding["review_resolution"] == {
        "decision_id": SENIOR_AUTUMN_TRIPLE_CROWN_DECISION["decision_id"],
        "action": "lock",
        "target_vi": "Senior Autumn Triple Crown",
    }
    assert finding["canonical_resolution"] == {
        "layer": "community",
        "term_id": SENIOR_AUTUMN_TRIPLE_CROWN["id"],
        "target_vi": "Senior Autumn Triple Crown",
    }


def test_senior_autumn_triple_crown_does_not_resolve_other_source_file(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    finding = refresh_canonical_resolutions(
        tmp_path,
        {"schema_version": 1, "findings": [_finding("localize_dict.json")]},
    )["findings"][0]
    assert finding["review_resolution"]["action"] == "lock"
    assert finding["canonical_resolution"] is None

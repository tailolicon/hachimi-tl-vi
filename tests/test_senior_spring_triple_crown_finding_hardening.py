from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import refresh_canonical_resolutions
from scripts.harden_senior_spring_triple_crown_finding import (
    SENIOR_SPRING_TRIPLE_CROWN,
    SENIOR_SPRING_TRIPLE_CROWN_DECISION,
    harden,
)


def _seed(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    (glossary / "ui_community_terms.json").write_text(json.dumps({"schema_version": 1, "terms": []}), encoding="utf-8")
    (glossary / "terminology_reviews.json").write_text(json.dumps({"schema_version": 1, "decisions": []}), encoding="utf-8")
    (glossary / "term_registry.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "source_bridge_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")


def test_senior_spring_triple_crown_resolves_category_111(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False
    reviews = json.loads((tmp_path / "glossary" / "terminology_reviews.json").read_text(encoding="utf-8"))
    decision = next(item for item in reviews["decisions"] if item["decision_id"] == SENIOR_SPRING_TRIPLE_CROWN_DECISION["decision_id"])
    assert decision["target_vi"] == "Senior Spring Triple Crown"
    ledger = {"schema_version": 1, "findings": [{
        "finding_id": "cf-90f54108327ec3e8", "status": "open", "source_zh_cn": "春古马三冠",
        "match_mode": "exact", "source_paths": ["text_data_dict.json"], "key_exact": [],
        "json_path_prefixes": [["111"]], "suggested_targets_vi": [],
        "canonical_resolution": None, "review_resolution": None,
    }]}
    finding = refresh_canonical_resolutions(tmp_path, ledger)["findings"][0]
    assert finding["review_resolution"]["target_vi"] == "Senior Spring Triple Crown"
    assert finding["canonical_resolution"] == {
        "layer": "community",
        "term_id": SENIOR_SPRING_TRIPLE_CROWN["id"],
        "target_vi": "Senior Spring Triple Crown",
    }


def test_senior_spring_triple_crown_does_not_resolve_other_category(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    ledger = {"schema_version": 1, "findings": [{
        "finding_id": "cf-test-spring-crown-wrong", "status": "open", "source_zh_cn": "春古马三冠",
        "match_mode": "exact", "source_paths": ["text_data_dict.json"], "key_exact": [],
        "json_path_prefixes": [["112"]], "suggested_targets_vi": [],
        "canonical_resolution": None, "review_resolution": None,
    }]}
    assert refresh_canonical_resolutions(tmp_path, ledger)["findings"][0]["canonical_resolution"] is None

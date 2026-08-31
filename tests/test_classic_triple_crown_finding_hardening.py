from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import refresh_canonical_resolutions
from scripts.harden_classic_triple_crown_finding import CLASSIC_TRIPLE_CROWN, CLASSIC_TRIPLE_CROWN_DECISION, harden


def test_classic_triple_crown_hardener_resolves_finding(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    (glossary / "ui_community_terms.json").write_text(json.dumps({"schema_version": 1, "terms": []}), encoding="utf-8")
    (glossary / "terminology_reviews.json").write_text(json.dumps({"schema_version": 1, "decisions": []}), encoding="utf-8")
    (glossary / "term_registry.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "source_bridge_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")

    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    community = json.loads((glossary / "ui_community_terms.json").read_text(encoding="utf-8"))
    term = next(item for item in community["terms"] if item["id"] == CLASSIC_TRIPLE_CROWN["id"])
    assert term["preferred"] == "Classic Triple Crown"
    assert term["source_paths"] == ["localize_dict.json"]
    assert term["match_mode"] == "exact"

    reviews = json.loads((glossary / "terminology_reviews.json").read_text(encoding="utf-8"))
    decision = next(item for item in reviews["decisions"] if item["decision_id"] == CLASSIC_TRIPLE_CROWN_DECISION["decision_id"])
    assert decision["target_vi"] == "Classic Triple Crown"

    ledger = {"schema_version": 1, "findings": [{
        "finding_id": "cf-test-classic-triple-crown",
        "status": "open",
        "source_zh_cn": "经典三冠",
        "match_mode": "exact",
        "source_paths": ["localize_dict.json"],
        "key_exact": [],
        "json_path_prefixes": [],
        "suggested_targets_vi": [],
        "canonical_resolution": None,
        "review_resolution": None,
    }]}
    finding = refresh_canonical_resolutions(tmp_path, ledger)["findings"][0]
    assert finding["canonical_resolution"] == {
        "layer": "community",
        "term_id": CLASSIC_TRIPLE_CROWN["id"],
        "target_vi": "Classic Triple Crown",
    }

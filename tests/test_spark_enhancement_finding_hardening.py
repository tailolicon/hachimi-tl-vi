from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import refresh_canonical_resolutions
from scripts.harden_spark_enhancement_finding import SPARK_ENHANCEMENT, SPARK_ENHANCEMENT_DECISION, harden


def test_spark_enhancement_hardener_resolves_finding(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    (glossary / "ui_community_terms.json").write_text(json.dumps({"schema_version": 1, "terms": []}), encoding="utf-8")
    (glossary / "terminology_reviews.json").write_text(json.dumps({"schema_version": 1, "decisions": []}), encoding="utf-8")
    (glossary / "term_registry.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "source_bridge_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")

    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    community = json.loads((glossary / "ui_community_terms.json").read_text(encoding="utf-8"))
    term = next(item for item in community["terms"] if item["id"] == SPARK_ENHANCEMENT["id"])
    assert term["preferred"] == "Spark Enhancement"
    assert term["source_paths"] == ["text_data_dict.json"]
    assert term["match_mode"] == "contains"

    reviews = json.loads((glossary / "terminology_reviews.json").read_text(encoding="utf-8"))
    decision = next(item for item in reviews["decisions"] if item["decision_id"] == SPARK_ENHANCEMENT_DECISION["decision_id"])
    assert decision["target_vi"] == "Spark Enhancement"

    ledger = {"schema_version": 1, "findings": [{
        "finding_id": "cf-test-spark-enhancement",
        "status": "open",
        "source_zh_cn": "因子强化",
        "match_mode": "contains",
        "source_paths": ["text_data_dict.json"],
        "key_exact": [],
        "json_path_prefixes": [],
        "suggested_targets_vi": [],
        "canonical_resolution": None,
        "review_resolution": None,
    }]}
    finding = refresh_canonical_resolutions(tmp_path, ledger)["findings"][0]
    assert finding["canonical_resolution"] == {
        "layer": "community",
        "term_id": SPARK_ENHANCEMENT["id"],
        "target_vi": "Spark Enhancement",
    }

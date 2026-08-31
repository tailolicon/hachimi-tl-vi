from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import refresh_canonical_resolutions
from scripts.harden_derby_stallion_masters_finding import (
    DERBY_STALLION_MASTERS,
    DERBY_STALLION_MASTERS_DECISION,
    harden,
)


def _seed(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    (glossary / "ui_community_terms.json").write_text(json.dumps({"schema_version": 1, "terms": []}), encoding="utf-8")
    (glossary / "terminology_reviews.json").write_text(json.dumps({"schema_version": 1, "decisions": []}), encoding="utf-8")
    (glossary / "term_registry.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "source_bridge_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")


def test_derby_stallion_masters_resolves_collaboration_descriptions(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False
    reviews = json.loads((tmp_path / "glossary" / "terminology_reviews.json").read_text(encoding="utf-8"))
    decision = next(item for item in reviews["decisions"] if item["decision_id"] == DERBY_STALLION_MASTERS_DECISION["decision_id"])
    assert decision["target_vi"] == "Derby Stallion Masters"
    ledger = {"schema_version": 1, "findings": [{
        "finding_id": "cf-c443cdb477c9c443", "status": "open", "source_zh_cn": "ダービースタリオン マスターズ",
        "match_mode": "contains", "source_paths": ["text_data_dict.json"], "key_exact": [],
        "json_path_prefixes": [], "suggested_targets_vi": ["Derby Stallion Masters"],
        "canonical_resolution": None, "review_resolution": None,
    }]}
    finding = refresh_canonical_resolutions(tmp_path, ledger)["findings"][0]
    assert finding["review_resolution"]["target_vi"] == "Derby Stallion Masters"
    assert finding["canonical_resolution"] == {
        "layer": "community", "term_id": DERBY_STALLION_MASTERS["id"], "target_vi": "Derby Stallion Masters"
    }


def test_derby_stallion_masters_does_not_resolve_other_text_category(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    ledger = {"schema_version": 1, "findings": [{
        "finding_id": "cf-test-dabimas-wrong", "status": "open", "source_zh_cn": "ダービースタリオン マスターズ",
        "match_mode": "contains", "source_paths": ["text_data_dict.json"], "key_exact": [],
        "json_path_prefixes": [["16"]], "suggested_targets_vi": ["Derby Stallion Masters"],
        "canonical_resolution": None, "review_resolution": None,
    }]}
    assert refresh_canonical_resolutions(tmp_path, ledger)["findings"][0]["canonical_resolution"] is None

from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import refresh_canonical_resolutions
from scripts.harden_triple_tiara_finding import TRIPLE_TIARA, TRIPLE_TIARA_DECISION, harden


def _seed(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    (glossary / "ui_community_terms.json").write_text(json.dumps({"schema_version": 1, "terms": []}), encoding="utf-8")
    (glossary / "terminology_reviews.json").write_text(json.dumps({"schema_version": 1, "decisions": []}), encoding="utf-8")
    (glossary / "term_registry.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "source_bridge_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")


def test_triple_tiara_resolves_only_the_audited_category(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False
    community = json.loads((tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8"))
    rule = next(item for item in community["terms"] if item["id"] == TRIPLE_TIARA["id"])
    assert rule["preferred"] == "Triple Tiara"
    assert rule["json_path_prefixes"] == [["144"]]
    reviews = json.loads((tmp_path / "glossary" / "terminology_reviews.json").read_text(encoding="utf-8"))
    decision = next(item for item in reviews["decisions"] if item["decision_id"] == TRIPLE_TIARA_DECISION["decision_id"])
    assert decision["target_vi"] == "Triple Tiara"
    ledger = {"schema_version": 1, "findings": [{
        "finding_id": "cf-test-triple-tiara", "status": "open", "source_zh_cn": "三后冠",
        "match_mode": "contains", "source_paths": ["text_data_dict.json"], "key_exact": [],
        "json_path_prefixes": [["144"]], "suggested_targets_vi": ["Triple Tiara"],
        "canonical_resolution": None, "review_resolution": None,
    }]}
    finding = refresh_canonical_resolutions(tmp_path, ledger)["findings"][0]
    assert finding["review_resolution"]["target_vi"] == "Triple Tiara"
    assert finding["canonical_resolution"] == {"layer": "community", "term_id": "achievement.triple_tiara", "target_vi": "Triple Tiara"}


def test_triple_tiara_does_not_resolve_outside_category_144(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    ledger = {"schema_version": 1, "findings": [{
        "finding_id": "cf-test-triple-tiara-wrong", "status": "open", "source_zh_cn": "三后冠",
        "match_mode": "contains", "source_paths": ["text_data_dict.json"], "key_exact": [],
        "json_path_prefixes": [["163"]], "suggested_targets_vi": ["Triple Tiara"],
        "canonical_resolution": None, "review_resolution": None,
    }]}
    assert refresh_canonical_resolutions(tmp_path, ledger)["findings"][0]["canonical_resolution"] is None

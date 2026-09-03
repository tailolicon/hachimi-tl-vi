from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import refresh_canonical_resolutions
from scripts.harden_ryota_fujii_finding import DECISION, TERM, harden


def _seed(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    (glossary / "ui_community_terms.json").write_text(json.dumps({"schema_version": 1, "terms": []}), encoding="utf-8")
    (glossary / "terminology_reviews.json").write_text(json.dumps({"schema_version": 1, "decisions": []}), encoding="utf-8")
    (glossary / "term_registry.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "source_bridge_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")


def _finding(prefix: str, *, source_path: str = "text_data_dict.json") -> dict:
    return {
        "finding_id": "cf-71b93369404bbe81",
        "status": "open",
        "source_zh_cn": "藤井亮太",
        "match_mode": "contains",
        "source_paths": [source_path],
        "key_exact": [],
        "json_path_prefixes": [[prefix]],
        "suggested_targets_vi": [],
        "canonical_resolution": None,
        "review_resolution": None,
    }


def test_hardener_resolves_ryota_fujii_credit_and_is_idempotent(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    community = json.loads((tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8"))
    rule = next(item for item in community["terms"] if item["id"] == TERM["id"])
    assert rule["preferred"] == "Ryota Fujii"
    assert rule["json_path_prefixes"] == [["17"]]
    assert rule["match_mode"] == "contains"
    assert "藤井亮太" in rule["forbidden"]

    reviews = json.loads((tmp_path / "glossary" / "terminology_reviews.json").read_text(encoding="utf-8"))
    decision = next(item for item in reviews["decisions"] if item["decision_id"] == DECISION["decision_id"])
    assert decision["target_vi"] == "Ryota Fujii"

    finding = refresh_canonical_resolutions(tmp_path, {"schema_version": 1, "findings": [_finding("17")]})["findings"][0]
    assert finding["canonical_resolution"] == {
        "layer": "community",
        "term_id": "proper_name.ryota_fujii.credit17",
        "target_vi": "Ryota Fujii",
    }


def test_rule_does_not_resolve_same_name_outside_credit_scope(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    outside_category = refresh_canonical_resolutions(
        tmp_path, {"schema_version": 1, "findings": [_finding("147")]}
    )["findings"][0]
    assert outside_category["canonical_resolution"] is None

    outside_file = refresh_canonical_resolutions(
        tmp_path, {"schema_version": 1, "findings": [_finding("17", source_path="localize_dict.json")]}
    )["findings"][0]
    assert outside_file["canonical_resolution"] is None

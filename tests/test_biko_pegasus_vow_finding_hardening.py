from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import refresh_canonical_resolutions
from scripts.harden_biko_pegasus_vow_finding import VOW_FAMILY, VOW_TERMS, harden


def _seed(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    (glossary / "ui_community_terms.json").write_text(json.dumps({"schema_version": 1, "terms": []}), encoding="utf-8")
    (glossary / "terminology_reviews.json").write_text(json.dumps({"schema_version": 1, "decisions": []}), encoding="utf-8")
    (glossary / "term_registry.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "source_bridge_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")


def _family_finding(prefix: str = "142") -> dict:
    return {
        "finding_id": "cf-test-biko-vow-family",
        "status": "open",
        "source_zh_cn": "热血誓言",
        "match_mode": "contains",
        "source_paths": ["text_data_dict.json"],
        "key_exact": [],
        "json_path_prefixes": [[prefix]],
        "suggested_targets_vi": [],
        "canonical_resolution": None,
        "review_resolution": None,
    }


def test_hardener_resolves_family_and_exact_variants(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    community = json.loads((tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8"))
    family = next(item for item in community["terms"] if item["id"] == VOW_FAMILY["id"])
    assert family["preferred"] == "Passionate Vow"
    assert "不可动摇的热血誓言・短距离" in family["exclude_source_contains"]

    expected = {
        "热血誓言・短距离": "Passionate Vow - Sprint",
        "不可动摇的热血誓言・短距离": "Unyielding Vow - Sprint",
        "热血誓言・英里": "Passionate Vow - Mile",
        "不可动摇的热血誓言・英里": "Unyielding Vow - Mile",
    }
    for source, target in expected.items():
        term = next(item for item in VOW_TERMS if source in item["source_aliases"])
        stored = next(item for item in community["terms"] if item["id"] == term["id"])
        assert stored["preferred"] == target
        assert stored["match_mode"] == "exact"
        assert stored["json_path_prefixes"] == [["142"]]

    finding = refresh_canonical_resolutions(tmp_path, {"schema_version": 1, "findings": [_family_finding()]})["findings"][0]
    assert finding["review_resolution"]["target_vi"] == "Passionate Vow"
    assert finding["canonical_resolution"] == {
        "layer": "community",
        "term_id": "condition.biko_pegasus.passionate_vow.family",
        "target_vi": "Passionate Vow",
    }


def test_family_rule_does_not_escape_condition_table(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    finding = refresh_canonical_resolutions(tmp_path, {"schema_version": 1, "findings": [_family_finding("147")]})["findings"][0]
    assert finding["canonical_resolution"] is None

from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import active_findings, refresh_canonical_resolutions
from scripts.harden_biko_pegasus_unyielding_prefix_finding import DECISION, SOURCE, harden
from scripts.harden_biko_pegasus_vow_finding import VOW_TERMS

FINDING_ID = "cf-5026b367a0d84413"


def _seed(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    (glossary / "terminology_reviews.json").write_text(
        json.dumps({"schema_version": 1, "decisions": []}), encoding="utf-8"
    )
    (glossary / "ui_community_terms.json").write_text(
        json.dumps({"schema_version": 1, "terms": list(VOW_TERMS)}), encoding="utf-8"
    )
    (glossary / "term_registry.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "source_bridge_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "skill_name_style.json").write_text(json.dumps({"canonical_examples": []}), encoding="utf-8")


def _finding() -> dict:
    return {
        "finding_id": FINDING_ID,
        "status": "open",
        "source_zh_cn": SOURCE,
        "match_mode": "contains",
        "source_paths": ["text_data_dict.json"],
        "key_exact": [],
        "json_path_prefixes": [],
        "suggested_targets_vi": [],
        "canonical_resolution": None,
        "review_resolution": None,
    }


def test_unyielding_prefix_is_ignored_without_collapsing_exact_variants(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    reviews = json.loads((tmp_path / "glossary" / "terminology_reviews.json").read_text(encoding="utf-8"))
    decision = next(item for item in reviews["decisions"] if item["decision_id"] == DECISION["decision_id"])
    assert decision["action"] == "ignore"
    assert decision["source_zh_cn"] == SOURCE
    assert decision["source_paths"] == ["text_data_dict.json"]
    assert decision["json_path_prefixes"] == [["142"]]
    assert decision["match_mode"] == "contains"

    resolved = refresh_canonical_resolutions(tmp_path, {"schema_version": 1, "findings": [_finding()]})
    row = resolved["findings"][0]
    assert row["canonical_resolution"] is None
    assert row["review_resolution"]["action"] == "ignore"
    assert active_findings(resolved) == []

    exact_targets = {term["source_aliases"][0]: term["preferred"] for term in VOW_TERMS}
    assert exact_targets["不可动摇的热血誓言・短距离"] == "Unyielding Vow - Sprint"
    assert exact_targets["不可动摇的热血誓言・英里"] == "Unyielding Vow - Mile"


def test_unrelated_path_does_not_receive_ignore_resolution(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    finding = _finding()
    finding["source_paths"] = ["localize_dict.json"]
    resolved = refresh_canonical_resolutions(tmp_path, {"schema_version": 1, "findings": [finding]})
    assert resolved["findings"][0]["review_resolution"] is None

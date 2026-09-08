from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import refresh_canonical_resolutions
from scripts.harden_mejiro_ramonu_tokenu_yuime_finding import DECISION, RULE, harden


def _seed(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    (glossary / "ui_community_terms.json").write_text(json.dumps({"schema_version": 1, "terms": []}), encoding="utf-8")
    (glossary / "terminology_reviews.json").write_text(json.dumps({"schema_version": 1, "decisions": []}), encoding="utf-8")
    (glossary / "term_registry.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "source_bridge_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    finding = {
        "finding_id": "cf-03735d8f77de39a1",
        "status": "open",
        "source_zh_cn": "至死不渝的爱",
        "match_mode": "contains",
        "source_paths": ["text_data_dict.json"],
        "key_exact": [],
        "json_path_prefixes": [["172"]],
        "suggested_targets_vi": [],
        "canonical_resolution": None,
        "review_resolution": None,
    }
    (glossary / "canonical_findings.json").write_text(json.dumps({"schema_version": 1, "findings": [finding]}), encoding="utf-8")


def test_hardener_restores_verified_skill_identity_and_is_idempotent(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    community = json.loads((tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8"))
    rule = next(item for item in community["terms"] if item["id"] == RULE["id"])
    assert rule["preferred"] == "解けぬ結い目"
    assert rule["json_path_prefixes"] == [["172"]]
    assert rule["match_mode"] == "contains"

    reviews = json.loads((tmp_path / "glossary" / "terminology_reviews.json").read_text(encoding="utf-8"))
    decision = next(item for item in reviews["decisions"] if item["decision_id"] == DECISION["decision_id"])
    assert decision["target_vi"] == "解けぬ結い目"

    findings = json.loads((tmp_path / "glossary" / "canonical_findings.json").read_text(encoding="utf-8"))
    refreshed = refresh_canonical_resolutions(tmp_path, findings)["findings"][0]
    assert refreshed["canonical_resolution"] == {
        "layer": "community",
        "term_id": RULE["id"],
        "target_vi": "解けぬ結い目",
    }


def test_rule_does_not_resolve_same_alias_outside_inheritance_category(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    findings = json.loads((tmp_path / "glossary" / "canonical_findings.json").read_text(encoding="utf-8"))
    findings["findings"][0]["json_path_prefixes"] = [["147"]]
    refreshed = refresh_canonical_resolutions(tmp_path, findings)["findings"][0]
    assert refreshed["canonical_resolution"] is None

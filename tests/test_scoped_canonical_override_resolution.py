from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import refresh_canonical_resolutions
from scripts.resolve_scoped_canonical_overrides import resolve_scoped_canonical_overrides


def _seed(tmp_path: Path, *, scoped: bool = True) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    rule = {
        "id": "stat.stamina.achievement_threshold",
        "source_aliases": ["体力"],
        "preferred": "Stamina",
        "accepted": ["Stamina"],
        "match_mode": "contains",
        "source_paths": ["text_data_dict.json"],
    }
    if scoped:
        rule["json_path_prefixes"] = [["131"]]
    (glossary / "ui_community_terms.json").write_text(json.dumps({"schema_version": 1, "terms": [rule]}), encoding="utf-8")
    (glossary / "terminology_reviews.json").write_text(json.dumps({
        "schema_version": 1,
        "decisions": [{
            "decision_id": "existing.energy",
            "source_zh_cn": "体力",
            "action": "lock",
            "target_vi": "Energy",
            "kind": "terminology",
        }],
    }), encoding="utf-8")
    (glossary / "term_registry.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "source_bridge_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")


def _finding(prefix: str = "131") -> dict:
    return {
        "finding_id": "cf-test-scoped-override",
        "status": "open",
        "source_zh_cn": "体力",
        "match_mode": "contains",
        "source_paths": ["text_data_dict.json"],
        "key_exact": [],
        "json_path_prefixes": [[prefix]],
        "suggested_targets_vi": [],
        "canonical_resolution": None,
        "review_resolution": None,
    }


def test_scoped_community_rule_can_override_generic_review_lock(tmp_path: Path) -> None:
    _seed(tmp_path)
    ledger = refresh_canonical_resolutions(tmp_path, {"schema_version": 1, "findings": [_finding()]})
    assert ledger["findings"][0]["review_resolution"]["target_vi"] == "Energy"
    assert ledger["findings"][0]["canonical_resolution"] is None

    ledger = resolve_scoped_canonical_overrides(tmp_path, ledger)
    assert ledger["findings"][0]["canonical_resolution"] == {
        "layer": "community",
        "term_id": "stat.stamina.achievement_threshold",
        "target_vi": "Stamina",
    }


def test_scoped_override_must_cover_finding_scope(tmp_path: Path) -> None:
    _seed(tmp_path)
    ledger = refresh_canonical_resolutions(tmp_path, {"schema_version": 1, "findings": [_finding("143")]})
    ledger = resolve_scoped_canonical_overrides(tmp_path, ledger)
    assert ledger["findings"][0]["canonical_resolution"] is None


def test_unscoped_community_rule_cannot_override_review_lock(tmp_path: Path) -> None:
    _seed(tmp_path, scoped=False)
    ledger = refresh_canonical_resolutions(tmp_path, {"schema_version": 1, "findings": [_finding()]})
    ledger = resolve_scoped_canonical_overrides(tmp_path, ledger)
    assert ledger["findings"][0]["canonical_resolution"] is None

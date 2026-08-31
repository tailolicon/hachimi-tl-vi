from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import refresh_canonical_resolutions
from scripts.harden_stamina_threshold_finding import OBSOLETE_DECISION_ID, STAMINA_THRESHOLD, harden
from scripts.resolve_scoped_canonical_overrides import resolve_scoped_canonical_overrides


def _seed(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    (glossary / "ui_community_terms.json").write_text(json.dumps({"schema_version": 1, "terms": []}), encoding="utf-8")
    (glossary / "terminology_reviews.json").write_text(json.dumps({
        "schema_version": 1,
        "decisions": [
            {
                "decision_id": "existing.energy",
                "source_zh_cn": "体力",
                "action": "lock",
                "target_vi": "Energy",
                "kind": "terminology",
            },
            {
                "decision_id": OBSOLETE_DECISION_ID,
                "source_zh_cn": "体力",
                "action": "lock",
                "target_vi": "Stamina",
                "kind": "terminology",
            },
        ],
    }), encoding="utf-8")
    (glossary / "term_registry.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "source_bridge_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")


def _finding(prefix: str) -> dict:
    return {
        "finding_id": "cf-test-stamina-threshold",
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


def _resolve(tmp_path: Path, prefix: str) -> dict:
    ledger = refresh_canonical_resolutions(tmp_path, {"schema_version": 1, "findings": [_finding(prefix)]})
    return resolve_scoped_canonical_overrides(tmp_path, ledger)["findings"][0]


def test_hardener_resolves_category_131_stamina_threshold_and_is_idempotent(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    community = json.loads((tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8"))
    rule = next(item for item in community["terms"] if item["id"] == STAMINA_THRESHOLD["id"])
    assert rule["preferred"] == "Stamina"
    assert rule["json_path_prefixes"] == [["131"]]

    reviews = json.loads((tmp_path / "glossary" / "terminology_reviews.json").read_text(encoding="utf-8"))
    assert reviews["decisions"] == [{
        "decision_id": "existing.energy",
        "source_zh_cn": "体力",
        "action": "lock",
        "target_vi": "Energy",
        "kind": "terminology",
    }]

    finding = _resolve(tmp_path, "131")
    assert finding["review_resolution"]["target_vi"] == "Energy"
    assert finding["canonical_resolution"] == {
        "layer": "community",
        "term_id": "stat.stamina.achievement_threshold",
        "target_vi": "Stamina",
    }


def test_rule_does_not_override_energy_outside_achievement_category(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    finding = _resolve(tmp_path, "143")
    assert finding["review_resolution"]["target_vi"] == "Energy"
    assert finding["canonical_resolution"] is None

from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import refresh_canonical_resolutions
from scripts.harden_hero_radiance_finding import HERO_RADIANCE, harden


def _seed(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    (glossary / "ui_community_terms.json").write_text(json.dumps({"schema_version": 1, "terms": []}), encoding="utf-8")
    (glossary / "terminology_reviews.json").write_text(json.dumps({"schema_version": 1, "decisions": []}), encoding="utf-8")
    (glossary / "term_registry.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "source_bridge_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")


def _finding(prefix: str) -> dict:
    return {
        "finding_id": "cf-test-hero-radiance",
        "status": "open",
        "source_zh_cn": "英雄的光辉",
        "match_mode": "exact",
        "source_paths": ["text_data_dict.json"],
        "key_exact": [],
        "json_path_prefixes": [[prefix]],
        "suggested_targets_vi": [],
        "canonical_resolution": None,
        "review_resolution": None,
    }


def test_hardener_resolves_zenno_rob_roy_condition_and_is_idempotent(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    community = json.loads((tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8"))
    rule = next(item for item in community["terms"] if item["id"] == HERO_RADIANCE["id"])
    assert rule["preferred"] == "Hero's Radiance"
    assert rule["source_paths"] == ["text_data_dict.json"]
    assert rule["json_path_prefixes"] == [["142"]]
    assert rule["match_mode"] == "exact"

    finding = refresh_canonical_resolutions(tmp_path, {"schema_version": 1, "findings": [_finding("142")]})["findings"][0]
    assert finding["review_resolution"]["target_vi"] == "Hero's Radiance"
    assert finding["canonical_resolution"] == {
        "layer": "community",
        "term_id": "condition.zenno_rob_roy.heros_radiance",
        "target_vi": "Hero's Radiance",
    }


def test_rule_does_not_resolve_same_text_outside_condition_table(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    finding = refresh_canonical_resolutions(tmp_path, {"schema_version": 1, "findings": [_finding("147")]})["findings"][0]
    assert finding["canonical_resolution"] is None

from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import refresh_canonical_resolutions
from scripts.harden_masamichi_nagai_finding import DECISION, TERM, harden


def _seed(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    (glossary / "ui_community_terms.json").write_text(json.dumps({"schema_version": 1, "terms": []}), encoding="utf-8")
    (glossary / "terminology_reviews.json").write_text(json.dumps({"schema_version": 1, "decisions": []}), encoding="utf-8")
    (glossary / "source_bridge_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "term_registry.json").write_text(json.dumps({
        "terms": [{
            "id": "skill.righteous_path",
            "source_aliases": ["正道"],
            "preferred": "Chính đạo",
            "accepted": ["Chính đạo"],
            "source_paths": ["text_data_dict.json"],
            "match_mode": "contains",
            "exclude_source_contains": ["永井正道"]
        }]
    }), encoding="utf-8")


def _finding(*, source_path: str = "text_data_dict.json") -> dict:
    return {
        "finding_id": "cf-1bd479584e40d767",
        "status": "open",
        "source_zh_cn": "永井正道",
        "match_mode": "contains",
        "source_paths": [source_path],
        "key_exact": [],
        "json_path_prefixes": [],
        "suggested_targets_vi": [],
        "canonical_resolution": None,
        "review_resolution": None,
    }


def test_hardener_resolves_creator_name_without_skill_alias_overmatch(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    community = json.loads((tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8"))
    rule = next(item for item in community["terms"] if item["id"] == TERM["id"])
    assert rule["preferred"] == "Masamichi Nagai"
    assert rule["source_paths"] == ["text_data_dict.json"]
    assert rule["match_mode"] == "contains"

    reviews = json.loads((tmp_path / "glossary" / "terminology_reviews.json").read_text(encoding="utf-8"))
    decision = next(item for item in reviews["decisions"] if item["decision_id"] == DECISION["decision_id"])
    assert decision["target_vi"] == "Masamichi Nagai"

    finding = refresh_canonical_resolutions(tmp_path, {"schema_version": 1, "findings": [_finding()]})["findings"][0]
    assert finding["canonical_resolution"] == {
        "layer": "community",
        "term_id": "proper_name.masamichi_nagai",
        "target_vi": "Masamichi Nagai",
    }

    registry = json.loads((tmp_path / "glossary" / "term_registry.json").read_text(encoding="utf-8"))
    skill = next(item for item in registry["terms"] if item["id"] == "skill.righteous_path")
    assert "永井正道" in skill["exclude_source_contains"]


def test_full_name_rule_does_not_cover_other_source_file(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    finding = refresh_canonical_resolutions(
        tmp_path, {"schema_version": 1, "findings": [_finding(source_path="localize_dict.json")]}
    )["findings"][0]
    assert finding["canonical_resolution"] is None

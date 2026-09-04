from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import refresh_canonical_resolutions
from scripts.harden_champions_meeting_newline_finding import DECISION, TERM, harden


def _seed(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    (glossary / "ui_community_terms.json").write_text(json.dumps({"schema_version": 1, "terms": []}), encoding="utf-8")
    (glossary / "terminology_reviews.json").write_text(json.dumps({"schema_version": 1, "decisions": []}), encoding="utf-8")
    (glossary / "term_registry.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "source_bridge_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")


def _finding(*, source: str = "群英\n月赛", source_path: str = "localize_dict.json") -> dict:
    return {
        "finding_id": "cf-1de7f10f817c5866",
        "status": "open",
        "source_zh_cn": source,
        "match_mode": "exact",
        "source_paths": [source_path],
        "key_exact": [],
        "json_path_prefixes": [],
        "suggested_targets_vi": [],
        "canonical_resolution": None,
        "review_resolution": None,
    }


def test_hardener_resolves_exact_newline_alias_and_is_idempotent(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    community = json.loads((tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8"))
    rule = next(item for item in community["terms"] if item["id"] == TERM["id"])
    assert rule["preferred"] == "Champions Meeting"
    assert rule["source_aliases"] == ["群英\n月赛"]
    assert rule["source_paths"] == ["localize_dict.json"]
    assert rule["match_mode"] == "exact"

    reviews = json.loads((tmp_path / "glossary" / "terminology_reviews.json").read_text(encoding="utf-8"))
    decision = next(item for item in reviews["decisions"] if item["decision_id"] == DECISION["decision_id"])
    assert decision["target_vi"] == "Champions Meeting"

    finding = refresh_canonical_resolutions(tmp_path, {"schema_version": 1, "findings": [_finding()]})["findings"][0]
    assert finding["canonical_resolution"] == {
        "layer": "community",
        "term_id": "event.champions_meeting.localize_newline",
        "target_vi": "Champions Meeting",
    }


def test_rule_does_not_resolve_flattened_or_other_file_variant(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True

    flattened = refresh_canonical_resolutions(
        tmp_path, {"schema_version": 1, "findings": [_finding(source="群英月赛")]}
    )["findings"][0]
    assert flattened["canonical_resolution"] is None

    other_file = refresh_canonical_resolutions(
        tmp_path, {"schema_version": 1, "findings": [_finding(source_path="text_data_dict.json")]}
    )["findings"][0]
    assert other_file["canonical_resolution"] is None

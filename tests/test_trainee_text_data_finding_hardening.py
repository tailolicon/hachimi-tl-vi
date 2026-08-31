from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import refresh_canonical_resolutions
from scripts.harden_trainee_text_data_finding import TRAINEE_TEXT_DATA, TRAINEE_TEXT_DATA_DECISION, harden


def _seed(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    (glossary / "ui_community_terms.json").write_text(json.dumps({"schema_version": 1, "terms": []}), encoding="utf-8")
    (glossary / "terminology_reviews.json").write_text(json.dumps({"schema_version": 1, "decisions": []}), encoding="utf-8")
    (glossary / "term_registry.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "source_bridge_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")


def _finding(source: str = "育成赛马娘") -> dict:
    return {
        "finding_id": "cf-338ec3f0de1ad2e9",
        "status": "open",
        "source_zh_cn": source,
        "match_mode": "contains",
        "source_paths": ["text_data_dict.json"],
        "key_exact": [],
        "json_path_prefixes": [],
        "suggested_targets_vi": ["Trainee"],
        "canonical_resolution": None,
        "review_resolution": None,
    }


def test_hardener_resolves_full_trainee_compound_and_is_idempotent(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    community = json.loads((tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8"))
    rule = next(item for item in community["terms"] if item["id"] == TRAINEE_TEXT_DATA["id"])
    assert rule["preferred"] == "Trainee"
    assert rule["source_paths"] == ["text_data_dict.json"]
    assert rule["json_path_prefixes"] == []
    assert rule["source_aliases"] == ["育成赛马娘"]

    reviews = json.loads((tmp_path / "glossary" / "terminology_reviews.json").read_text(encoding="utf-8"))
    decision = next(item for item in reviews["decisions"] if item["decision_id"] == TRAINEE_TEXT_DATA_DECISION["decision_id"])
    assert decision["target_vi"] == "Trainee"

    finding = refresh_canonical_resolutions(tmp_path, {"schema_version": 1, "findings": [_finding()]})["findings"][0]
    assert finding["canonical_resolution"] == {
        "layer": "community",
        "term_id": "career.ui.trainee.text_data",
        "target_vi": "Trainee",
    }


def test_rule_does_not_canonicalize_bare_umamusume_or_bare_career(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    for source in ("赛马娘", "育成"):
        finding = refresh_canonical_resolutions(tmp_path, {"schema_version": 1, "findings": [_finding(source)]})["findings"][0]
        assert finding["canonical_resolution"] is None

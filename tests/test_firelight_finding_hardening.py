from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import active_findings, refresh_canonical_resolutions
from scripts.harden_firelight_finding import DECISION, FINDING_ID, HISTORICAL_TARGET, RULE, SOURCE_JA, SOURCE_ZH, TARGET, harden


def _finding(*, source_path: str = "text_data_dict.json") -> dict:
    return {"finding_id": FINDING_ID, "status": "open", "source_zh_cn": SOURCE_ZH, "match_mode": "contains", "source_paths": [source_path], "key_exact": [], "json_path_prefixes": [["172"]], "suggested_targets_vi": [], "canonical_resolution": None, "review_resolution": None}


def _seed(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    for name, payload in {
        "ui_community_terms.json": {"schema_version": 1, "terms": []},
        "terminology_reviews.json": {"schema_version": 1, "decisions": []},
        "canonical_findings.json": {"schema_version": 1, "findings": [_finding()]},
        "term_registry.json": {"terms": []},
        "source_bridge_terms.json": {"terms": []},
        "skill_name_style.json": {"canonical_examples": []},
    }.items():
        (glossary / name).write_text(json.dumps(payload), encoding="utf-8")


def test_hardener_resolves_firelight_and_is_idempotent(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False
    community = json.loads((tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8"))
    rule = next(item for item in community["terms"] if item["id"] == RULE["id"])
    assert rule["preferred"] == TARGET
    assert rule["accepted"] == [TARGET]
    assert HISTORICAL_TARGET in rule["forbidden"]
    reviews = json.loads((tmp_path / "glossary" / "terminology_reviews.json").read_text(encoding="utf-8"))
    decision = next(item for item in reviews["decisions"] if item["decision_id"] == DECISION["decision_id"])
    assert decision["ja"] == [SOURCE_JA]
    resolved = refresh_canonical_resolutions(tmp_path, json.loads((tmp_path / "glossary" / "canonical_findings.json").read_text(encoding="utf-8")))
    assert resolved["findings"][0]["canonical_resolution"] == {"layer": "community", "term_id": RULE["id"], "target_vi": TARGET}
    assert active_findings(resolved) == []


def test_rule_does_not_cover_wrong_source_path(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    wrong = _finding(source_path="localize_dict.json")
    wrong["suggested_targets_vi"] = [TARGET]
    assert refresh_canonical_resolutions(tmp_path, {"schema_version": 1, "findings": [wrong]})["findings"][0]["canonical_resolution"] is None

from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import active_findings, refresh_canonical_resolutions
from scripts.harden_symboli_rudolf_divine_might_finding import (
    DECISION_ID,
    FINDING_ID,
    RULE_ID,
    SOURCE_JA,
    SOURCE_ZH,
    TARGET,
    harden,
)


def _seed(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    (glossary / "ui_community_terms.json").write_text(
        json.dumps({"schema_version": 1, "terms": []}), encoding="utf-8"
    )
    (glossary / "terminology_reviews.json").write_text(
        json.dumps({"schema_version": 1, "decisions": []}), encoding="utf-8"
    )
    (glossary / "term_registry.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "source_bridge_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "skill_name_style.json").write_text(
        json.dumps({"canonical_examples": []}), encoding="utf-8"
    )


def _finding(source: str = SOURCE_ZH) -> dict[str, object]:
    return {
        "finding_id": FINDING_ID,
        "status": "open",
        "source_zh_cn": source,
        "match_mode": "exact",
        "source_paths": ["text_data_dict.json"],
        "key_exact": [],
        "json_path_prefixes": [],
        "suggested_targets_vi": [],
        "canonical_resolution": None,
        "review_resolution": None,
    }


def test_divine_might_resolves_live_finding_and_is_idempotent(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    community = json.loads((tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8"))
    rule = next(item for item in community["terms"] if item["id"] == RULE_ID)
    assert rule["preferred"] == TARGET
    assert rule["source_aliases"] == [SOURCE_ZH]
    assert rule["source_paths"] == ["text_data_dict.json"]
    assert rule["match_mode"] == "exact"

    reviews = json.loads((tmp_path / "glossary" / "terminology_reviews.json").read_text(encoding="utf-8"))
    decision = next(item for item in reviews["decisions"] if item["decision_id"] == DECISION_ID)
    assert decision["ja"] == [SOURCE_JA]
    assert decision["target_vi"] == TARGET

    payload = refresh_canonical_resolutions(
        tmp_path, {"schema_version": 1, "findings": [_finding()]}
    )
    finding = payload["findings"][0]
    assert finding["review_resolution"] == {
        "decision_id": DECISION_ID,
        "action": "lock",
        "target_vi": TARGET,
    }
    assert finding["canonical_resolution"] == {
        "layer": "community",
        "term_id": RULE_ID,
        "target_vi": TARGET,
    }
    assert active_findings(payload) == []


def test_divine_might_rule_is_exact_and_does_not_match_longer_prose(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    payload = refresh_canonical_resolutions(
        tmp_path,
        {"schema_version": 1, "findings": [_finding(source=f"继承「{SOURCE_ZH}」技能")]},
    )
    finding = payload["findings"][0]
    assert finding["canonical_resolution"] is None
    assert active_findings(payload) == [finding]

from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import refresh_canonical_resolutions
from scripts.harden_kaishin_step_finding import (
    FINDING_ID,
    KAISHIN_STEP,
    KAISHIN_STEP_DECISION,
    PREFERRED,
    SOURCE_ZH,
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


def _finding(
    *,
    source: str = SOURCE_ZH,
    source_path: str = "text_data_dict.json",
    suggested: list[str] | None = None,
) -> dict[str, object]:
    return {
        "finding_id": FINDING_ID,
        "status": "open",
        "source_zh_cn": source,
        "match_mode": "exact",
        "source_paths": [source_path],
        "key_exact": [],
        "json_path_prefixes": [],
        "suggested_targets_vi": list(suggested or []),
        "canonical_resolution": None,
        "review_resolution": None,
    }


def test_kaishin_step_resolves_live_finding(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    community = json.loads(
        (tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8")
    )
    rule = next(item for item in community["terms"] if item["id"] == KAISHIN_STEP["id"])
    assert rule["preferred"] == PREFERRED
    assert rule["source_paths"] == ["text_data_dict.json"]
    assert rule["match_mode"] == "exact"
    assert "Bước quyết tâm" in rule["forbidden"]

    reviews = json.loads(
        (tmp_path / "glossary" / "terminology_reviews.json").read_text(encoding="utf-8")
    )
    decision = next(
        item
        for item in reviews["decisions"]
        if item["decision_id"] == KAISHIN_STEP_DECISION["decision_id"]
    )
    assert decision["target_vi"] == PREFERRED
    assert decision["ja"] == ["会心の一歩"]

    ledger = {"schema_version": 1, "findings": [_finding()]}
    finding = refresh_canonical_resolutions(tmp_path, ledger)["findings"][0]
    assert finding["review_resolution"] == {
        "decision_id": "audit.finding.skill-kaishin-step",
        "action": "lock",
        "target_vi": PREFERRED,
    }
    assert finding["canonical_resolution"] == {
        "layer": "community",
        "term_id": "skill.kaishin_step",
        "target_vi": PREFERRED,
    }


def test_kaishin_step_rule_does_not_resolve_longer_source(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True

    ledger = {
        "schema_version": 1,
        "findings": [
            _finding(source=f"前缀{SOURCE_ZH}后缀", suggested=[PREFERRED]),
        ],
    }
    finding = refresh_canonical_resolutions(tmp_path, ledger)["findings"][0]
    assert finding["canonical_resolution"] is None


def test_kaishin_step_rule_does_not_resolve_other_source_path(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True

    ledger = {
        "schema_version": 1,
        "findings": [
            _finding(source_path="localize_dict.json"),
        ],
    }
    finding = refresh_canonical_resolutions(tmp_path, ledger)["findings"][0]
    assert finding["review_resolution"]["target_vi"] == PREFERRED
    assert finding["canonical_resolution"] is None

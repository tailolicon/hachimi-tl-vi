from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import refresh_canonical_resolutions
from scripts.harden_champions_meeting_leagues_finding import (
    DECISIONS,
    GRADED_FINDING_ID,
    GRADED_SOURCE,
    GRADED_TARGET,
    OPEN_FINDING_ID,
    OPEN_SOURCE,
    OPEN_TARGET,
    TERMS,
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


def _finding(finding_id: str, source: str, *, source_path: str = "localize_dict.json") -> dict[str, object]:
    return {
        "finding_id": finding_id,
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


def test_champions_meeting_leagues_resolve_live_findings(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    community = json.loads(
        (tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8")
    )
    by_id = {item["id"]: item for item in community["terms"]}
    assert by_id[TERMS[0]["id"]]["preferred"] == OPEN_TARGET
    assert by_id[TERMS[0]["id"]]["match_mode"] == "exact"
    assert by_id[TERMS[1]["id"]]["preferred"] == GRADED_TARGET
    assert by_id[TERMS[1]["id"]]["match_mode"] == "exact"

    reviews = json.loads(
        (tmp_path / "glossary" / "terminology_reviews.json").read_text(encoding="utf-8")
    )
    by_decision = {item["decision_id"]: item for item in reviews["decisions"]}
    assert by_decision[DECISIONS[0]["decision_id"]]["target_vi"] == OPEN_TARGET
    assert by_decision[DECISIONS[1]["decision_id"]]["target_vi"] == GRADED_TARGET

    ledger = {
        "schema_version": 1,
        "findings": [
            _finding(OPEN_FINDING_ID, OPEN_SOURCE),
            _finding(GRADED_FINDING_ID, GRADED_SOURCE),
        ],
    }
    findings = refresh_canonical_resolutions(tmp_path, ledger)["findings"]
    assert findings[0]["review_resolution"] == {
        "decision_id": "audit.finding.champions-meeting-open-league",
        "action": "lock",
        "target_vi": OPEN_TARGET,
    }
    assert findings[0]["canonical_resolution"] == {
        "layer": "community",
        "term_id": "event.champions_meeting.open_league",
        "target_vi": OPEN_TARGET,
    }
    assert findings[1]["review_resolution"] == {
        "decision_id": "audit.finding.champions-meeting-graded-league",
        "action": "lock",
        "target_vi": GRADED_TARGET,
    }
    assert findings[1]["canonical_resolution"] == {
        "layer": "community",
        "term_id": "event.champions_meeting.graded_league",
        "target_vi": GRADED_TARGET,
    }


def test_champions_meeting_league_rules_do_not_overmatch_longer_sources(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True

    ledger = {
        "schema_version": 1,
        "findings": [
            _finding("cf-long-open", f"前缀{OPEN_SOURCE}后缀"),
            _finding("cf-long-graded", f"前缀{GRADED_SOURCE}后缀"),
        ],
    }
    findings = refresh_canonical_resolutions(tmp_path, ledger)["findings"]
    assert findings[0]["canonical_resolution"] is None
    assert findings[1]["canonical_resolution"] is None


def test_champions_meeting_league_rules_do_not_resolve_other_source_path(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True

    ledger = {
        "schema_version": 1,
        "findings": [
            _finding(OPEN_FINDING_ID, OPEN_SOURCE, source_path="text_data_dict.json"),
            _finding(GRADED_FINDING_ID, GRADED_SOURCE, source_path="text_data_dict.json"),
        ],
    }
    findings = refresh_canonical_resolutions(tmp_path, ledger)["findings"]
    assert findings[0]["review_resolution"]["target_vi"] == OPEN_TARGET
    assert findings[0]["canonical_resolution"] is None
    assert findings[1]["review_resolution"]["target_vi"] == GRADED_TARGET
    assert findings[1]["canonical_resolution"] is None

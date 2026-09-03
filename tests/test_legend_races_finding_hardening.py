from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import refresh_canonical_resolutions
from scripts.harden_legend_races_finding import (
    DAILY_FINDING_ID,
    DAILY_KEY,
    DAILY_SOURCE,
    DAILY_TARGET,
    LEGEND_FINDING_ID,
    LEGEND_KEY,
    LEGEND_SOURCE,
    LEGEND_TARGET,
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
    finding_id: str,
    source: str,
    key: str,
    *,
    source_path: str = "localize_dict.json",
) -> dict[str, object]:
    return {
        "finding_id": finding_id,
        "status": "open",
        "source_zh_cn": source,
        "match_mode": "contains",
        "source_paths": [source_path],
        "key_exact": [key],
        "json_path_prefixes": [],
        "suggested_targets_vi": [],
        "canonical_resolution": None,
        "review_resolution": None,
    }


def test_legend_race_rules_resolve_item_scoped_findings(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    ledger = {
        "schema_version": 1,
        "findings": [
            _finding(LEGEND_FINDING_ID, LEGEND_SOURCE, LEGEND_KEY),
            _finding(DAILY_FINDING_ID, DAILY_SOURCE, DAILY_KEY),
        ],
    }
    findings = refresh_canonical_resolutions(tmp_path, ledger)["findings"]

    assert findings[0]["canonical_resolution"] == {
        "layer": "community",
        "term_id": "event.legend_race.transfer_notice",
        "target_vi": LEGEND_TARGET,
    }
    assert findings[0]["review_resolution"] == {
        "decision_id": "audit.finding.legend-race-transfer-notice",
        "action": "lock",
        "target_vi": LEGEND_TARGET,
    }
    assert findings[1]["canonical_resolution"] == {
        "layer": "community",
        "term_id": "event.daily_legend_race.transfer_notice",
        "target_vi": DAILY_TARGET,
    }
    assert findings[1]["review_resolution"] == {
        "decision_id": "audit.finding.daily-legend-race-transfer-notice",
        "action": "lock",
        "target_vi": DAILY_TARGET,
    }


def test_legend_race_rules_do_not_cover_other_keys(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True

    ledger = {
        "schema_version": 1,
        "findings": [
            _finding("cf-other-legend", LEGEND_SOURCE, "OtherKey"),
            _finding("cf-other-daily", DAILY_SOURCE, "OtherKey"),
        ],
    }
    findings = refresh_canonical_resolutions(tmp_path, ledger)["findings"]
    assert findings[0]["canonical_resolution"] is None
    assert findings[1]["canonical_resolution"] is None


def test_legend_race_rules_do_not_cover_other_source_path(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True

    ledger = {
        "schema_version": 1,
        "findings": [
            _finding(LEGEND_FINDING_ID, LEGEND_SOURCE, LEGEND_KEY, source_path="text_data_dict.json"),
            _finding(DAILY_FINDING_ID, DAILY_SOURCE, DAILY_KEY, source_path="text_data_dict.json"),
        ],
    }
    findings = refresh_canonical_resolutions(tmp_path, ledger)["findings"]
    assert findings[0]["canonical_resolution"] is None
    assert findings[1]["canonical_resolution"] is None

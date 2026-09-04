from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import active_findings, refresh_canonical_resolutions
from scripts.harden_air_messiah_bloodline_future_finding import (
    AIR_MESSIAH_BLOODLINE_FUTURE,
    AIR_MESSIAH_BLOODLINE_FUTURE_DECISION,
    AIR_MESSIAH_BLOODLINE_FUTURE_INHERITED_DECISION,
    FINDING_ID,
    INHERITED_FINDING_ID,
    PREFERRED,
    SOURCE_JA,
    SOURCE_ZH,
    SOURCE_ZH_INHERITED,
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
    finding_id: str = FINDING_ID,
    source_path: str = "text_data_dict.json",
) -> dict[str, object]:
    return {
        "finding_id": finding_id,
        "status": "open",
        "source_zh_cn": source,
        "match_mode": "contains",
        "source_paths": [source_path],
        "key_exact": [],
        "json_path_prefixes": [],
        "suggested_targets_vi": [],
        "canonical_resolution": None,
        "review_resolution": None,
    }


def test_air_messiah_unique_skill_resolves_standalone_and_inherited_findings(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    community = json.loads((tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8"))
    rule = next(item for item in community["terms"] if item["id"] == AIR_MESSIAH_BLOODLINE_FUTURE["id"])
    assert rule["preferred"] == PREFERRED
    assert rule["source_paths"] == ["text_data_dict.json"]
    assert rule["match_mode"] == "contains"
    assert rule["source_aliases"] == [SOURCE_ZH, SOURCE_ZH_INHERITED]
    assert "Huyết mạch nương tựa, tương lai Nở rộ" in rule["forbidden"]

    reviews = json.loads((tmp_path / "glossary" / "terminology_reviews.json").read_text(encoding="utf-8"))
    decisions = {item["decision_id"]: item for item in reviews["decisions"]}
    assert decisions[AIR_MESSIAH_BLOODLINE_FUTURE_DECISION["decision_id"]]["target_vi"] == PREFERRED
    assert decisions[AIR_MESSIAH_BLOODLINE_FUTURE_DECISION["decision_id"]]["ja"] == [SOURCE_JA]
    assert decisions[AIR_MESSIAH_BLOODLINE_FUTURE_INHERITED_DECISION["decision_id"]]["source_zh_cn"] == SOURCE_ZH_INHERITED
    assert decisions[AIR_MESSIAH_BLOODLINE_FUTURE_INHERITED_DECISION["decision_id"]]["target_vi"] == PREFERRED

    ledger = {
        "schema_version": 1,
        "findings": [
            _finding(),
            _finding(source=SOURCE_ZH_INHERITED, finding_id=INHERITED_FINDING_ID),
        ],
    }
    refreshed = refresh_canonical_resolutions(tmp_path, ledger)
    standalone, inherited = refreshed["findings"]
    assert standalone["review_resolution"] == {
        "decision_id": "audit.finding.skill-air-messiah-bloodline-future",
        "action": "lock",
        "target_vi": PREFERRED,
    }
    assert inherited["review_resolution"] == {
        "decision_id": "audit.finding.skill-air-messiah-bloodline-future-inherited-alias",
        "action": "lock",
        "target_vi": PREFERRED,
    }
    for finding in (standalone, inherited):
        assert finding["canonical_resolution"] == {
            "layer": "community",
            "term_id": "skill.air_messiah.bloodline_future",
            "target_vi": PREFERRED,
        }
    assert active_findings(refreshed) == []


def test_air_messiah_rule_resolves_alias_inside_longer_finding_source(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    ledger = {
        "schema_version": 1,
        "findings": [_finding(source=f"前缀{SOURCE_ZH_INHERITED}后缀", finding_id=INHERITED_FINDING_ID)],
    }
    finding = refresh_canonical_resolutions(tmp_path, ledger)["findings"][0]
    assert finding["canonical_resolution"] == {
        "layer": "community",
        "term_id": "skill.air_messiah.bloodline_future",
        "target_vi": PREFERRED,
    }


def test_air_messiah_rule_does_not_resolve_other_source_path(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    ledger = {
        "schema_version": 1,
        "findings": [
            _finding(
                source=SOURCE_ZH_INHERITED,
                finding_id=INHERITED_FINDING_ID,
                source_path="localize_dict.json",
            )
        ],
    }
    finding = refresh_canonical_resolutions(tmp_path, ledger)["findings"][0]
    assert finding["review_resolution"]["target_vi"] == PREFERRED
    assert finding["canonical_resolution"] is None

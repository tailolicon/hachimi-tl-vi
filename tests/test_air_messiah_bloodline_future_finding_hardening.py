from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import active_findings, refresh_canonical_resolutions
from scripts.harden_air_messiah_bloodline_future_finding import (
    AIR_MESSIAH_BLOODLINE_FUTURE,
    AIR_MESSIAH_BLOODLINE_FUTURE_DECISION,
    FINDING_ID,
    PREFERRED,
    SOURCE_JA,
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


def _finding(*, source: str = SOURCE_ZH, source_path: str = "text_data_dict.json") -> dict[str, object]:
    return {
        "finding_id": FINDING_ID,
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


def test_air_messiah_unique_skill_resolves_live_finding_shape(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    community = json.loads((tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8"))
    rule = next(item for item in community["terms"] if item["id"] == AIR_MESSIAH_BLOODLINE_FUTURE["id"])
    assert rule["preferred"] == PREFERRED
    assert rule["source_paths"] == ["text_data_dict.json"]
    assert rule["match_mode"] == "exact"
    assert "Huyết mạch nương tựa, tương lai Nở rộ" in rule["forbidden"]

    reviews = json.loads((tmp_path / "glossary" / "terminology_reviews.json").read_text(encoding="utf-8"))
    decision = next(
        item
        for item in reviews["decisions"]
        if item["decision_id"] == AIR_MESSIAH_BLOODLINE_FUTURE_DECISION["decision_id"]
    )
    assert decision["target_vi"] == PREFERRED
    assert decision["ja"] == [SOURCE_JA]

    ledger = {"schema_version": 1, "findings": [_finding()]}
    refreshed = refresh_canonical_resolutions(tmp_path, ledger)
    finding = refreshed["findings"][0]
    assert finding["review_resolution"] == {
        "decision_id": "audit.finding.skill-air-messiah-bloodline-future",
        "action": "lock",
        "target_vi": PREFERRED,
    }
    assert finding["canonical_resolution"] == {
        "layer": "community",
        "term_id": "skill.air_messiah.bloodline_future",
        "target_vi": PREFERRED,
    }
    assert active_findings(refreshed) == []


def test_air_messiah_rule_does_not_overmatch_longer_source(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    ledger = {"schema_version": 1, "findings": [_finding(source=f"前缀{SOURCE_ZH}后缀")]}
    finding = refresh_canonical_resolutions(tmp_path, ledger)["findings"][0]
    assert finding["canonical_resolution"] is None


def test_air_messiah_rule_does_not_resolve_other_source_path(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    ledger = {"schema_version": 1, "findings": [_finding(source_path="localize_dict.json")]}
    finding = refresh_canonical_resolutions(tmp_path, ledger)["findings"][0]
    assert finding["review_resolution"]["target_vi"] == PREFERRED
    assert finding["canonical_resolution"] is None

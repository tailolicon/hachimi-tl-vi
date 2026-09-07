from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import active_findings, refresh_canonical_resolutions
from scripts.harden_neo_universe_ad_astra_finding import (
    FINDING_IDS,
    HISTORICAL_TARGET,
    RULE,
    SOURCE_JA,
    SOURCE_ZH,
    TARGET,
    harden,
)


def _finding(
    *,
    source: str = SOURCE_ZH,
    source_path: str = "text_data_dict.json",
    match_mode: str = "contains",
) -> dict:
    return {
        "finding_id": FINDING_IDS[0],
        "status": "open",
        "source_zh_cn": source,
        "match_mode": match_mode,
        "source_paths": [source_path],
        "key_exact": [],
        "json_path_prefixes": [["172"]],
        "suggested_targets_vi": [],
        "canonical_resolution": None,
        "review_resolution": {"decision_id": "parallel.ctx-old", "action": "defer", "target_vi": None},
    }


def _seed(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    (glossary / "ui_community_terms.json").write_text(
        json.dumps({"schema_version": 1, "terms": []}), encoding="utf-8"
    )
    (glossary / "terminology_reviews.json").write_text(
        json.dumps({"schema_version": 1, "decisions": []}), encoding="utf-8"
    )
    (glossary / "canonical_findings.json").write_text(
        json.dumps({"schema_version": 1, "findings": [_finding()]}), encoding="utf-8"
    )
    (glossary / "term_registry.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "source_bridge_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "skill_name_style.json").write_text(
        json.dumps({"canonical_examples": []}), encoding="utf-8"
    )


def test_hardener_locks_ad_astra_and_resolves_live_finding(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    community = json.loads(
        (tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8")
    )
    rule = next(item for item in community["terms"] if item["id"] == RULE["id"])
    assert rule["preferred"] == TARGET
    assert rule["accepted"] == [TARGET]
    assert HISTORICAL_TARGET in rule["forbidden"]
    assert rule["match_mode"] == "exact"
    assert rule["source_paths"] == ["text_data_dict.json"]

    reviews = json.loads(
        (tmp_path / "glossary" / "terminology_reviews.json").read_text(encoding="utf-8")
    )
    decision = next(
        item for item in reviews["decisions"]
        if item["decision_id"] == "audit.finding.skill-neo-universe-ad-astra"
    )
    assert decision["ja"] == [SOURCE_JA]
    assert decision["target_vi"] == TARGET

    ledger = json.loads(
        (tmp_path / "glossary" / "canonical_findings.json").read_text(encoding="utf-8")
    )
    resolved_ledger = refresh_canonical_resolutions(tmp_path, ledger)
    resolved = resolved_ledger["findings"][0]
    assert resolved["suggested_targets_vi"] == [TARGET]
    assert resolved["canonical_resolution"] == {
        "layer": "community",
        "term_id": "skill.neo_universe.ad_astra",
        "target_vi": TARGET,
    }
    assert resolved["review_resolution"] == {
        "decision_id": "audit.finding.skill-neo-universe-ad-astra",
        "action": "lock",
        "target_vi": TARGET,
    }
    assert active_findings(resolved_ledger) == []


def test_exact_skill_alias_does_not_overmatch_other_alias_or_file(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True

    other_alias = _finding(source=f"前缀{SOURCE_ZH}后缀")
    other_alias["suggested_targets_vi"] = [TARGET]
    resolved = refresh_canonical_resolutions(
        tmp_path, {"schema_version": 1, "findings": [other_alias]}
    )["findings"][0]
    assert resolved["canonical_resolution"] is None

    outside = _finding(source_path="localize_dict.json")
    outside["suggested_targets_vi"] = [TARGET]
    resolved = refresh_canonical_resolutions(
        tmp_path, {"schema_version": 1, "findings": [outside]}
    )["findings"][0]
    assert resolved["canonical_resolution"] is None

from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import active_findings, refresh_canonical_resolutions
from scripts.harden_search_for_gold_finding import (
    FINDING_ID,
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
) -> dict:
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


def test_hardener_resolves_search_for_gold_and_is_idempotent(tmp_path: Path) -> None:
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
    assert "json_path_prefixes" not in rule

    reviews = json.loads(
        (tmp_path / "glossary" / "terminology_reviews.json").read_text(encoding="utf-8")
    )
    decision = next(
        item for item in reviews["decisions"]
        if item["decision_id"] == "audit.finding.skill-ougane-wo-tazunete-search-for-gold"
    )
    assert decision["ja"] == [SOURCE_JA]
    assert decision["target_vi"] == TARGET
    assert decision["source_paths"] == ["text_data_dict.json"]

    ledger = json.loads(
        (tmp_path / "glossary" / "canonical_findings.json").read_text(encoding="utf-8")
    )
    resolved_ledger = refresh_canonical_resolutions(tmp_path, ledger)
    resolved = resolved_ledger["findings"][0]
    assert resolved["suggested_targets_vi"] == [TARGET]
    assert resolved["canonical_resolution"] == {
        "layer": "community",
        "term_id": "skill.ougane_wo_tazunete.search_for_gold",
        "target_vi": TARGET,
    }
    assert resolved["review_resolution"] == {
        "decision_id": "audit.finding.skill-ougane-wo-tazunete-search-for-gold",
        "action": "lock",
        "target_vi": TARGET,
    }
    assert active_findings(resolved_ledger) == []


def test_rule_is_exact_and_does_not_overmatch_other_paths_or_prose(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True

    wrong_path = _finding(source_path="localize_dict.json")
    wrong_path["suggested_targets_vi"] = [TARGET]
    resolved_path = refresh_canonical_resolutions(
        tmp_path, {"schema_version": 1, "findings": [wrong_path]}
    )["findings"][0]
    assert resolved_path["canonical_resolution"] is None

    prose = _finding(source="寻访黄金的旅途")
    prose["suggested_targets_vi"] = [TARGET]
    resolved_prose = refresh_canonical_resolutions(
        tmp_path, {"schema_version": 1, "findings": [prose]}
    )["findings"][0]
    assert resolved_prose["canonical_resolution"] is None

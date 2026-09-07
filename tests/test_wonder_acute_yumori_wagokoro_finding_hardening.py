from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import active_findings, refresh_canonical_resolutions
from scripts.harden_wonder_acute_yumori_wagokoro_finding import (
    FINDING_IDS,
    HISTORICAL_TARGET,
    RULE,
    SOURCE_JA,
    SOURCE_ZH,
    SOURCE_ZH_PRIMARY,
    TARGET,
    TERM_ID,
    harden,
)


def _finding(
    *,
    source: str = SOURCE_ZH,
    source_path: str = "text_data_dict.json",
    match_mode: str = "exact",
) -> dict:
    return {
        "finding_id": FINDING_IDS[0],
        "status": "open",
        "source_zh_cn": source,
        "match_mode": match_mode,
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


def test_hardener_reuses_existing_canonical_skill_title_and_resolves_finding(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    community = json.loads(
        (tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8")
    )
    rule = next(item for item in community["terms"] if item["id"] == TERM_ID)
    assert rule["preferred"] == TARGET == "Tấm Lòng Người Giữ Suối Nóng"
    assert rule["accepted"] == [TARGET]
    assert rule["source_aliases"] == [SOURCE_ZH_PRIMARY, SOURCE_ZH]
    assert HISTORICAL_TARGET in rule["forbidden"]
    assert rule["match_mode"] == "contains"
    assert rule["source_paths"] == ["text_data_dict.json"]

    reviews = json.loads(
        (tmp_path / "glossary" / "terminology_reviews.json").read_text(encoding="utf-8")
    )
    decision = next(
        item for item in reviews["decisions"]
        if item["decision_id"] == "audit.finding.skill-wonder-acute-yumori-no-wagokoro"
    )
    assert decision["ja"] == [SOURCE_JA]
    assert decision["target_vi"] == TARGET
    assert decision["match_mode"] == "exact"

    ledger = json.loads(
        (tmp_path / "glossary" / "canonical_findings.json").read_text(encoding="utf-8")
    )
    resolved_ledger = refresh_canonical_resolutions(tmp_path, ledger)
    resolved = resolved_ledger["findings"][0]
    assert resolved["suggested_targets_vi"] == [TARGET]
    assert resolved["canonical_resolution"] == {
        "layer": "community",
        "term_id": TERM_ID,
        "target_vi": TARGET,
    }
    assert resolved["review_resolution"] == {
        "decision_id": "audit.finding.skill-wonder-acute-yumori-no-wagokoro",
        "action": "lock",
        "target_vi": TARGET,
    }
    assert active_findings(resolved_ledger) == []


def test_shared_skill_rule_does_not_match_other_source_file(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True

    outside = _finding(source_path="localize_dict.json")
    outside["suggested_targets_vi"] = [TARGET]
    resolved = refresh_canonical_resolutions(
        tmp_path, {"schema_version": 1, "findings": [outside]}
    )["findings"][0]
    assert resolved["canonical_resolution"] is None

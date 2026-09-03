from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import active_findings, refresh_canonical_resolutions
from scripts.harden_rhein_kraft_zutto_zutto_kagayaite_finding import (
    DECISION_ID,
    FINDING_ID,
    RULE_ID,
    SOURCE_JA,
    SOURCE_ZH,
    TARGET,
    harden,
)


def _finding(source: str = SOURCE_ZH, source_path: str = "text_data_dict.json") -> dict:
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
    glossary.mkdir(parents=True)
    for name, payload in {
        "ui_community_terms.json": {"schema_version": 1, "terms": []},
        "terminology_reviews.json": {"schema_version": 1, "decisions": []},
        "canonical_findings.json": {"schema_version": 1, "findings": [_finding()]},
        "term_registry.json": {"terms": []},
        "source_bridge_terms.json": {"terms": []},
        "skill_name_style.json": {"canonical_examples": []},
    }.items():
        (glossary / name).write_text(json.dumps(payload), encoding="utf-8")


def test_hardener_resolves_rhein_kraft_unique_skill_and_is_idempotent(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    community = json.loads((tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8"))
    rule = next(item for item in community["terms"] if item["id"] == RULE_ID)
    assert rule["preferred"] == TARGET
    assert rule["accepted"] == [TARGET]
    assert "Mãi mãi tỏa sáng" in rule["forbidden"]
    assert rule["match_mode"] == "contains"

    reviews = json.loads((tmp_path / "glossary" / "terminology_reviews.json").read_text(encoding="utf-8"))
    decision = next(item for item in reviews["decisions"] if item["decision_id"] == DECISION_ID)
    assert decision["ja"] == [SOURCE_JA]
    assert decision["target_vi"] == TARGET

    ledger = json.loads((tmp_path / "glossary" / "canonical_findings.json").read_text(encoding="utf-8"))
    finding = refresh_canonical_resolutions(tmp_path, ledger)["findings"][0]
    assert finding["suggested_targets_vi"] == [TARGET]
    assert finding["canonical_resolution"] == {"layer": "community", "term_id": RULE_ID, "target_vi": TARGET}
    assert finding["review_resolution"] == {"decision_id": DECISION_ID, "action": "lock", "target_vi": TARGET}
    assert active_findings({"schema_version": 1, "findings": [finding]}) == []


def test_contains_rule_covers_inheritance_text_but_not_other_file(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    longer = _finding(source=f"速度上限与力量上限提升，能获得「{SOURCE_ZH}」技能灵感的因子")
    longer["suggested_targets_vi"] = [TARGET]
    longer_resolved = refresh_canonical_resolutions(tmp_path, {"schema_version": 1, "findings": [longer]})["findings"][0]
    assert longer_resolved["canonical_resolution"] == {"layer": "community", "term_id": RULE_ID, "target_vi": TARGET}

    outside = _finding(source_path="localize_dict.json")
    outside["suggested_targets_vi"] = [TARGET]
    outside_resolved = refresh_canonical_resolutions(tmp_path, {"schema_version": 1, "findings": [outside]})["findings"][0]
    assert outside_resolved["canonical_resolution"] is None

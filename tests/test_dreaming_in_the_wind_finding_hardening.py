from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import active_findings, refresh_canonical_resolutions
from scripts.harden_dreaming_in_the_wind_finding import DECISION_ID, FINDING_ID, RULE_ID, SOURCE_JA, SOURCE_ZH, TARGET, harden


def _finding(source: str = SOURCE_ZH, source_path: str = "text_data_dict.json") -> dict:
    return {
        "finding_id": FINDING_ID,
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


def _seed(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir(parents=True)
    (glossary / "ui_community_terms.json").write_text(json.dumps({"schema_version": 1, "terms": []}), encoding="utf-8")
    (glossary / "terminology_reviews.json").write_text(json.dumps({"schema_version": 1, "decisions": []}), encoding="utf-8")
    (glossary / "canonical_findings.json").write_text(json.dumps({"schema_version": 1, "findings": [_finding()]}), encoding="utf-8")
    (glossary / "term_registry.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "source_bridge_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "skill_name_style.json").write_text(json.dumps({"canonical_examples": []}), encoding="utf-8")


def test_hardener_resolves_dreaming_in_the_wind_and_is_idempotent(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    community = json.loads((tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8"))
    rule = next(item for item in community["terms"] if item["id"] == RULE_ID)
    assert rule["preferred"] == TARGET
    assert rule["accepted"] == [TARGET]
    assert SOURCE_ZH in rule["source_aliases"]
    assert "Cuồng phong giấc mơ" in rule["forbidden"]
    assert rule["match_mode"] == "exact"
    assert rule["source_paths"] == ["text_data_dict.json"]

    reviews = json.loads((tmp_path / "glossary" / "terminology_reviews.json").read_text(encoding="utf-8"))
    decision = next(item for item in reviews["decisions"] if item["decision_id"] == DECISION_ID)
    assert decision["target_vi"] == TARGET
    assert decision["source_zh_cn"] == SOURCE_ZH
    assert decision["ja"] == [SOURCE_JA]

    ledger = json.loads((tmp_path / "glossary" / "canonical_findings.json").read_text(encoding="utf-8"))
    resolved_ledger = refresh_canonical_resolutions(tmp_path, ledger)
    resolved = resolved_ledger["findings"][0]
    assert resolved["suggested_targets_vi"] == [TARGET]
    assert resolved["canonical_resolution"] == {"layer": "community", "term_id": RULE_ID, "target_vi": TARGET}
    assert resolved["review_resolution"] == {"decision_id": DECISION_ID, "action": "lock", "target_vi": TARGET}
    assert active_findings(resolved_ledger) == []


def test_exact_rule_does_not_cover_longer_text_or_other_file(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True

    longer = _finding(source=f"歌曲《{SOURCE_ZH}》")
    longer["suggested_targets_vi"] = [TARGET]
    longer_resolved = refresh_canonical_resolutions(tmp_path, {"schema_version": 1, "findings": [longer]})["findings"][0]
    assert longer_resolved["canonical_resolution"] is None

    outside = _finding(source_path="localize_dict.json")
    outside["suggested_targets_vi"] = [TARGET]
    outside_resolved = refresh_canonical_resolutions(tmp_path, {"schema_version": 1, "findings": [outside]})["findings"][0]
    assert outside_resolved["canonical_resolution"] is None

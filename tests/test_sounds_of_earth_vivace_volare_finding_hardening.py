from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import active_findings, refresh_canonical_resolutions
from scripts.harden_sounds_of_earth_vivace_volare_finding import (
    FINDING_IDS,
    HISTORICAL_TARGETS,
    RULE,
    SOURCE_JA,
    SOURCE_ZH,
    TARGET,
    harden,
)
from scripts.translation_review_common import community_term_matches, load_community_terms


def _finding(
    finding_id: str,
    *,
    match_mode: str,
    json_path_prefixes: list[list[str]] | None = None,
    source_path: str = "text_data_dict.json",
) -> dict:
    return {
        "finding_id": finding_id,
        "status": "open",
        "source_zh_cn": SOURCE_ZH,
        "match_mode": match_mode,
        "source_paths": [source_path],
        "key_exact": [],
        "json_path_prefixes": json_path_prefixes or [],
        "suggested_targets_vi": [],
        "canonical_resolution": None,
        "review_resolution": {"decision_id": "legacy.defer", "action": "defer", "target_vi": None},
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
        json.dumps({
            "schema_version": 1,
            "findings": [
                _finding(FINDING_IDS[0], match_mode="contains", json_path_prefixes=[["172"]]),
                _finding(FINDING_IDS[1], match_mode="exact"),
            ],
        }, ensure_ascii=False),
        encoding="utf-8",
    )
    (glossary / "term_registry.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "source_bridge_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "skill_name_style.json").write_text(
        json.dumps({"canonical_examples": []}), encoding="utf-8"
    )


def test_hardener_locks_vivace_volare_for_title_and_factor_scopes(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    community = json.loads(
        (tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8")
    )
    rule = next(item for item in community["terms"] if item["id"] == RULE["id"])
    assert rule["preferred"] == TARGET
    assert rule["accepted"] == [TARGET]
    assert rule["forbidden"] == HISTORICAL_TARGETS
    assert rule["match_mode"] == "contains"
    assert rule["source_paths"] == ["text_data_dict.json"]

    reviews = json.loads(
        (tmp_path / "glossary" / "terminology_reviews.json").read_text(encoding="utf-8")
    )
    decision = next(
        item for item in reviews["decisions"]
        if item["decision_id"] == "audit.finding.skill-sounds-of-earth-vivace-volare"
    )
    assert decision["ja"] == [SOURCE_JA]
    assert decision["target_vi"] == TARGET

    ledger = json.loads(
        (tmp_path / "glossary" / "canonical_findings.json").read_text(encoding="utf-8")
    )
    resolved = refresh_canonical_resolutions(tmp_path, ledger)
    for finding in resolved["findings"]:
        assert finding["suggested_targets_vi"] == [TARGET]
        assert finding["canonical_resolution"] == {
            "layer": "community",
            "term_id": RULE["id"],
            "target_vi": TARGET,
        }
        assert finding["review_resolution"] == {
            "decision_id": "audit.finding.skill-sounds-of-earth-vivace-volare",
            "action": "lock",
            "target_vi": TARGET,
        }
    assert active_findings(resolved) == []


def test_runtime_rule_covers_embedded_factor_text_and_exact_title(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    terms = load_community_terms(tmp_path)

    title = community_term_matches(
        None,
        SOURCE_ZH,
        TARGET,
        terms,
        source_path="text_data_dict.json",
        json_path=["147", "11020101"],
    )
    title_rule = next(item for item in title if item["id"] == RULE["id"])
    assert title_rule["accepted_present"] is True
    assert title_rule["forbidden_present"] is False

    factor_source = f"耐力上限、力量上限和根性上限提升 ,\\n能获得「{SOURCE_ZH}」技能折扣的因子"
    factor_target = f"Giới hạn Stamina, Power và Guts tăng,\\nSpark giúp giảm giá Skill 「{TARGET}」"
    factor = community_term_matches(
        None,
        factor_source,
        factor_target,
        terms,
        source_path="text_data_dict.json",
        json_path=["172", "11020102"],
    )
    factor_rule = next(item for item in factor if item["id"] == RULE["id"])
    assert factor_rule["accepted_present"] is True
    assert factor_rule["forbidden_present"] is False


def test_rule_does_not_escape_text_data_file(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    outside = _finding(
        FINDING_IDS[0],
        match_mode="contains",
        json_path_prefixes=[["172"]],
        source_path="localize_dict.json",
    )
    outside["suggested_targets_vi"] = [TARGET]
    resolved = refresh_canonical_resolutions(
        tmp_path, {"schema_version": 1, "findings": [outside]}
    )["findings"][0]
    assert resolved["canonical_resolution"] is None

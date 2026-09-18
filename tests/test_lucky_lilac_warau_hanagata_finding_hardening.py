from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import active_findings, refresh_canonical_resolutions
from scripts.harden_lucky_lilac_warau_hanagata_finding import (
    FINDING_ID,
    RULE,
    SOURCE_JA,
    SOURCE_ZH,
    TARGET,
    harden,
)
from scripts.translation_review_common import community_term_matches, load_community_terms


def _finding(*, source_path: str = "text_data_dict.json") -> dict:
    return {
        "finding_id": FINDING_ID,
        "status": "open",
        "source_zh_cn": SOURCE_ZH,
        "match_mode": "contains",
        "source_paths": [source_path],
        "key_exact": [],
        "json_path_prefixes": [],
        "suggested_targets_vi": [],
        "canonical_resolution": None,
        "review_resolution": {
            "decision_id": "parallel.ctx-67f8551f77807292-v1.term-0073.16",
            "action": "defer",
            "target_vi": None,
        },
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
        json.dumps({"schema_version": 1, "findings": [_finding()]}, ensure_ascii=False),
        encoding="utf-8",
    )
    (glossary / "term_registry.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "source_bridge_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "skill_name_style.json").write_text(
        json.dumps({"canonical_examples": []}), encoding="utf-8"
    )


def test_hardener_locks_verified_lucky_lilac_skill_and_resolves_finding(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    community = json.loads(
        (tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8")
    )
    rule = next(item for item in community["terms"] if item["id"] == RULE["id"])
    assert rule["preferred"] == TARGET
    assert rule["accepted"] == [TARGET]
    assert rule["match_mode"] == "contains"
    assert rule["source_paths"] == ["text_data_dict.json"]

    reviews = json.loads(
        (tmp_path / "glossary" / "terminology_reviews.json").read_text(encoding="utf-8")
    )
    decision = next(
        item for item in reviews["decisions"]
        if item["decision_id"] == "audit.finding.skill-lucky-lilac-warau-hanagata"
    )
    assert decision["ja"] == [SOURCE_JA]
    assert decision["target_vi"] == TARGET

    ledger = json.loads(
        (tmp_path / "glossary" / "canonical_findings.json").read_text(encoding="utf-8")
    )
    resolved = refresh_canonical_resolutions(tmp_path, ledger)
    finding = resolved["findings"][0]
    assert finding["suggested_targets_vi"] == [TARGET]
    assert finding["canonical_resolution"] == {
        "layer": "community",
        "term_id": RULE["id"],
        "target_vi": TARGET,
    }
    assert finding["review_resolution"] == {
        "decision_id": "audit.finding.skill-lucky-lilac-warau-hanagata",
        "action": "lock",
        "target_vi": TARGET,
    }
    assert active_findings(resolved) == []


def test_rule_covers_exact_skill_title_and_inheritance_factor_text(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    terms = load_community_terms(tmp_path)

    title = community_term_matches(
        None,
        SOURCE_ZH,
        TARGET,
        terms,
        source_path="text_data_dict.json",
        json_path=["147", "11300101"],
    )
    title_rule = next(item for item in title if item["id"] == RULE["id"])
    assert title_rule["accepted_present"] is True

    factor_source = (
        f"力量上限、毅力上限与智力上限提升，\\n"
        f"可获得「{SOURCE_ZH}」技能灵感的因子"
    )
    factor_target = (
        f"Tăng giới hạn Power, Guts và Wit,\\n"
        f"Spark giúp nhận Skill Hint 「{TARGET}」"
    )
    factor = community_term_matches(
        None,
        factor_source,
        factor_target,
        terms,
        source_path="text_data_dict.json",
        json_path=["172", "11300103"],
    )
    factor_rule = next(item for item in factor if item["id"] == RULE["id"])
    assert factor_rule["accepted_present"] is True


def test_rule_does_not_escape_text_data_file(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    outside = _finding(source_path="localize_dict.json")
    outside["suggested_targets_vi"] = [TARGET]
    resolved = refresh_canonical_resolutions(
        tmp_path, {"schema_version": 1, "findings": [outside]}
    )["findings"][0]
    assert resolved["canonical_resolution"] is None

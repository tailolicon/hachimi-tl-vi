from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import active_findings, refresh_canonical_resolutions
from scripts.harden_air_shakur_found_you_finding import (
    FINDING_ID,
    HISTORICAL_TARGET,
    PATH_PREFIX,
    RULE,
    SOURCE_JA,
    SOURCE_ZH,
    TARGET,
    harden,
)


def _finding(*, source: str = SOURCE_ZH, source_path: str = "text_data_dict.json", prefix: list[str] | None = None) -> dict:
    return {
        "finding_id": FINDING_ID,
        "status": "open",
        "source_zh_cn": source,
        "match_mode": "contains",
        "source_paths": [source_path],
        "key_exact": [],
        "json_path_prefixes": [PATH_PREFIX if prefix is None else prefix],
        "suggested_targets_vi": [],
        "canonical_resolution": None,
        "review_resolution": None,
    }


def _seed(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    (glossary / "ui_community_terms.json").write_text(json.dumps({"schema_version": 1, "terms": []}), encoding="utf-8")
    (glossary / "terminology_reviews.json").write_text(json.dumps({"schema_version": 1, "decisions": []}), encoding="utf-8")
    (glossary / "canonical_findings.json").write_text(json.dumps({"schema_version": 1, "findings": [_finding()]}), encoding="utf-8")
    (glossary / "term_registry.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "source_bridge_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "skill_name_style.json").write_text(json.dumps({"canonical_examples": []}), encoding="utf-8")


def test_hardener_locks_original_jp_english_title_and_is_idempotent(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    community = json.loads((tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8"))
    rule = next(item for item in community["terms"] if item["id"] == RULE["id"])
    assert rule["preferred"] == TARGET
    assert rule["accepted"] == [TARGET]
    assert HISTORICAL_TARGET in rule["forbidden"]
    assert rule["source_paths"] == ["text_data_dict.json"]
    assert rule["json_path_prefixes"] == [PATH_PREFIX]
    assert rule["match_mode"] == "contains"

    reviews = json.loads((tmp_path / "glossary" / "terminology_reviews.json").read_text(encoding="utf-8"))
    decision = next(item for item in reviews["decisions"] if item["decision_id"] == "audit.finding.skill-air-shakur-found-you")
    assert decision["ja"] == [SOURCE_JA]
    assert decision["target_vi"] == TARGET
    assert decision["match_mode"] == "contains"

    ledger = json.loads((tmp_path / "glossary" / "canonical_findings.json").read_text(encoding="utf-8"))
    resolved_ledger = refresh_canonical_resolutions(tmp_path, ledger)
    resolved = resolved_ledger["findings"][0]
    assert resolved["suggested_targets_vi"] == [TARGET]
    assert resolved["canonical_resolution"] == {
        "layer": "community",
        "term_id": "skill.air_shakur_found_you",
        "target_vi": TARGET,
    }
    assert resolved["review_resolution"] == {
        "decision_id": "audit.finding.skill-air-shakur-found-you",
        "action": "lock",
        "target_vi": TARGET,
    }
    assert active_findings(resolved_ledger) == []


def test_rule_is_narrow_to_inheritance_category_and_rejects_old_calque(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert TARGET != HISTORICAL_TARGET

    wrong_path = _finding(source_path="localize_dict.json")
    wrong_path["suggested_targets_vi"] = [TARGET]
    assert refresh_canonical_resolutions(tmp_path, {"schema_version": 1, "findings": [wrong_path]})["findings"][0]["canonical_resolution"] is None

    wrong_prefix = _finding(prefix=["6"])
    wrong_prefix["suggested_targets_vi"] = [TARGET]
    assert refresh_canonical_resolutions(tmp_path, {"schema_version": 1, "findings": [wrong_prefix]})["findings"][0]["canonical_resolution"] is None

    prose = _finding(source="Skill khác ...抓到你了。 nhưng ngoài phạm vi", prefix=["6"])
    prose["suggested_targets_vi"] = [TARGET]
    assert refresh_canonical_resolutions(tmp_path, {"schema_version": 1, "findings": [prose]})["findings"][0]["canonical_resolution"] is None

from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import active_findings, refresh_canonical_resolutions
from scripts.harden_jidai_wo_kaeru_mono_finding import (
    DECISION,
    FINDING_ID,
    HISTORICAL_TARGETS,
    SOURCE_JA,
    SOURCE_ZH,
    TARGET,
    TERM,
    TERM_ID,
    harden,
)


def _finding(*, source_path: str = "text_data_dict.json", prefix: list[list[str]] | None = None) -> dict:
    return {
        "finding_id": FINDING_ID,
        "status": "open",
        "source_zh_cn": SOURCE_ZH,
        "match_mode": "exact",
        "source_paths": [source_path],
        "key_exact": [],
        "json_path_prefixes": prefix if prefix is not None else [["147"]],
        "suggested_targets_vi": [],
        "canonical_resolution": None,
        "review_resolution": None,
    }


def _seed(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    (glossary / "ui_community_terms.json").write_text(json.dumps({"schema_version": 1, "terms": []}), encoding="utf-8")
    (glossary / "terminology_reviews.json").write_text(json.dumps({"schema_version": 1, "decisions": []}), encoding="utf-8")
    # Seed the actual category-147 finding scope that the production rule is
    # intentionally allowed to cover. Negative scope behavior is exercised
    # separately below with category 172 and localize_dict.
    (glossary / "canonical_findings.json").write_text(json.dumps({"schema_version": 1, "findings": [_finding()]}), encoding="utf-8")
    (glossary / "term_registry.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "source_bridge_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "skill_name_style.json").write_text(json.dumps({"canonical_examples": []}), encoding="utf-8")


def test_hardener_resolves_jidai_wo_kaeru_mono_and_is_idempotent(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    community = json.loads((tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8"))
    rule = next(item for item in community["terms"] if item["id"] == TERM_ID)
    assert rule["preferred"] == TARGET
    assert rule["accepted"] == [TARGET]
    assert rule["forbidden"] == HISTORICAL_TARGETS
    assert rule["source_paths"] == ["text_data_dict.json"]
    assert rule["json_path_prefixes"] == [["147"]]
    assert rule["match_mode"] == "exact"

    reviews = json.loads((tmp_path / "glossary" / "terminology_reviews.json").read_text(encoding="utf-8"))
    decision = next(item for item in reviews["decisions"] if item["decision_id"] == DECISION["decision_id"])
    assert decision["ja"] == [SOURCE_JA]
    assert decision["target_vi"] == TARGET

    ledger = json.loads((tmp_path / "glossary" / "canonical_findings.json").read_text(encoding="utf-8"))
    resolved_ledger = refresh_canonical_resolutions(tmp_path, ledger)
    resolved = resolved_ledger["findings"][0]
    assert resolved["suggested_targets_vi"] == [TARGET]
    assert resolved["canonical_resolution"] == {
        "layer": "community",
        "term_id": TERM["id"],
        "target_vi": TARGET,
    }
    assert resolved["review_resolution"] == {
        "decision_id": DECISION["decision_id"],
        "action": "lock",
        "target_vi": TARGET,
    }
    assert active_findings(resolved_ledger) == []


def test_rule_does_not_escape_skill_title_category_or_source_file(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True

    wrong_category = _finding(prefix=[["172"]])
    wrong_category["suggested_targets_vi"] = [TARGET]
    resolved = refresh_canonical_resolutions(tmp_path, {"schema_version": 1, "findings": [wrong_category]})["findings"][0]
    assert resolved["canonical_resolution"] is None

    wrong_path = _finding(source_path="localize_dict.json")
    wrong_path["suggested_targets_vi"] = [TARGET]
    resolved = refresh_canonical_resolutions(tmp_path, {"schema_version": 1, "findings": [wrong_path]})["findings"][0]
    assert resolved["canonical_resolution"] is None

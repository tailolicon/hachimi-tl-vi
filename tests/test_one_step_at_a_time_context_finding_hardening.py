from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import active_findings, refresh_canonical_resolutions
from scripts.harden_one_step_at_a_time_context_finding import (
    DECISION_ID,
    FINDING_ID,
    LOCKED_TERM_ID,
    RULE_ID,
    SOURCE_JA,
    SOURCE_ZH,
    TARGET,
    harden,
)
from scripts.translation_review_common import load_locked_terms, locked_term_matches


def _finding(source_path: str = "text_data_dict.json", prefix: str = "147") -> dict:
    return {
        "finding_id": FINDING_ID,
        "status": "open",
        "source_zh_cn": SOURCE_ZH,
        "match_mode": "exact",
        "source_paths": [source_path],
        "key_exact": [],
        "json_path_prefixes": [[prefix]],
        "suggested_targets_vi": [],
        "canonical_resolution": None,
        "review_resolution": None,
    }


def _seed(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir(parents=True)
    (glossary / "term_registry.json").write_text(
        json.dumps({"terms": [{
            "id": LOCKED_TERM_ID,
            "zh_cn": ["前行"],
            "target_vi": "Nhắm Tuyến Đầu",
            "locked": True,
        }]}, ensure_ascii=False), encoding="utf-8"
    )
    (glossary / "ui_community_terms.json").write_text(
        json.dumps({"schema_version": 1, "terms": []}), encoding="utf-8"
    )
    (glossary / "terminology_reviews.json").write_text(
        json.dumps({"schema_version": 1, "decisions": []}), encoding="utf-8"
    )
    (glossary / "canonical_findings.json").write_text(
        json.dumps({"schema_version": 1, "findings": [_finding()]}), encoding="utf-8"
    )
    (glossary / "source_bridge_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "skill_name_style.json").write_text(json.dumps({"canonical_examples": []}), encoding="utf-8")


def test_hardener_scopes_frontline_target_and_resolves_distinct_skill(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    locked = load_locked_terms(tmp_path)
    assert locked_term_matches("前行", "Nhắm Tuyến Đầu", locked)[0]["id"] == LOCKED_TERM_ID
    assert locked_term_matches(
        SOURCE_ZH,
        "Tiến bước vững vàng",
        locked,
        source_path="text_data_dict.json",
        json_path=["147", "2033601"],
    ) == []

    community = json.loads((tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8"))
    rule = next(item for item in community["terms"] if item["id"] == RULE_ID)
    assert rule["preferred"] == TARGET
    assert rule["match_mode"] == "exact"
    assert rule["json_path_prefixes"] == [["147"]]

    reviews = json.loads((tmp_path / "glossary" / "terminology_reviews.json").read_text(encoding="utf-8"))
    decision = next(item for item in reviews["decisions"] if item["decision_id"] == DECISION_ID)
    assert decision["target_vi"] == TARGET
    assert decision["ja"] == [SOURCE_JA]

    ledger = json.loads((tmp_path / "glossary" / "canonical_findings.json").read_text(encoding="utf-8"))
    resolved = refresh_canonical_resolutions(tmp_path, ledger)
    finding = resolved["findings"][0]
    assert finding["suggested_targets_vi"] == [TARGET]
    assert finding["canonical_resolution"] == {
        "layer": "community",
        "term_id": RULE_ID,
        "target_vi": TARGET,
    }
    assert finding["review_resolution"] == {
        "decision_id": DECISION_ID,
        "action": "lock",
        "target_vi": TARGET,
    }
    assert active_findings(resolved) == []


def test_distinct_skill_rule_does_not_escape_category_147(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    outside = _finding(prefix="143")
    outside["suggested_targets_vi"] = [TARGET]
    resolved = refresh_canonical_resolutions(
        tmp_path, {"schema_version": 1, "findings": [outside]}
    )["findings"][0]
    assert resolved["canonical_resolution"] is None

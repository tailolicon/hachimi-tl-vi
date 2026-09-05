from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import active_findings, refresh_canonical_resolutions
from scripts.harden_trackblazer_start_of_climax_finding import (
    DECISION_ID,
    FINDING_ID,
    RULE_ID,
    SOURCE_JA,
    SOURCE_ZH,
    TARGET,
    harden,
)


def _seed(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    (glossary / "ui_community_terms.json").write_text(
        json.dumps({"schema_version": 1, "terms": []}), encoding="utf-8"
    )
    (glossary / "terminology_reviews.json").write_text(
        json.dumps({"schema_version": 1, "decisions": []}), encoding="utf-8"
    )
    (glossary / "term_registry.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "source_bridge_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "skill_name_style.json").write_text(
        json.dumps({"canonical_examples": []}), encoding="utf-8"
    )


def _finding(*, source_path: str = "text_data_dict.json") -> dict[str, object]:
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
        "review_resolution": None,
    }


def test_trackblazer_subtitle_resolves_live_finding_and_is_idempotent(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    community = json.loads((tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8"))
    rule = next(item for item in community["terms"] if item["id"] == RULE_ID)
    assert rule["preferred"] == TARGET
    assert rule["source_aliases"] == [SOURCE_ZH]
    assert rule["source_paths"] == ["text_data_dict.json"]
    assert rule["json_path_prefixes"] == []
    assert rule["match_mode"] == "contains"

    reviews = json.loads((tmp_path / "glossary" / "terminology_reviews.json").read_text(encoding="utf-8"))
    decision = next(item for item in reviews["decisions"] if item["decision_id"] == DECISION_ID)
    assert decision["ja"] == [SOURCE_JA]
    assert decision["target_vi"] == TARGET

    payload = refresh_canonical_resolutions(
        tmp_path, {"schema_version": 1, "findings": [_finding()]}
    )
    finding = payload["findings"][0]
    assert finding["review_resolution"] == {
        "decision_id": DECISION_ID,
        "action": "lock",
        "target_vi": TARGET,
    }
    assert finding["canonical_resolution"] == {
        "layer": "community",
        "term_id": RULE_ID,
        "target_vi": TARGET,
    }
    assert active_findings(payload) == []


def test_trackblazer_subtitle_rule_does_not_escape_text_data(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    payload = refresh_canonical_resolutions(
        tmp_path,
        {"schema_version": 1, "findings": [_finding(source_path="localize_dict.json")]},
    )
    finding = payload["findings"][0]
    assert finding["canonical_resolution"] is None
    assert active_findings(payload) == [finding]

from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import active_findings, refresh_canonical_resolutions
from scripts.harden_dream_journey_silver_world_finding import (
    DREAM_JOURNEY_SILVER_WORLD,
    DREAM_JOURNEY_SILVER_WORLD_DECISION,
    FINDING_ID,
    PREFERRED,
    SOURCE_JA,
    SOURCE_ZH,
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
        "review_resolution": {
            "decision_id": "parallel.ctx-67f8551f77807292-v1.term-0052.01",
            "action": "defer",
            "target_vi": None,
        },
    }


def test_dream_journey_unique_skill_resolves_inherited_finding(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    community = json.loads((tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8"))
    rule = next(item for item in community["terms"] if item["id"] == DREAM_JOURNEY_SILVER_WORLD["id"])
    assert rule["preferred"] == PREFERRED
    assert rule["source_paths"] == ["text_data_dict.json"]
    assert rule["match_mode"] == "contains"
    assert rule["source_aliases"] == [SOURCE_ZH]
    assert "Thế giới bạc trong giấc mơ" in rule["forbidden"]

    reviews = json.loads((tmp_path / "glossary" / "terminology_reviews.json").read_text(encoding="utf-8"))
    decision = next(
        item
        for item in reviews["decisions"]
        if item["decision_id"] == DREAM_JOURNEY_SILVER_WORLD_DECISION["decision_id"]
    )
    assert decision["target_vi"] == PREFERRED
    assert decision["ja"] == [SOURCE_JA]

    refreshed = refresh_canonical_resolutions(
        tmp_path,
        {"schema_version": 1, "findings": [_finding()]},
    )
    finding = refreshed["findings"][0]
    assert finding["review_resolution"] == {
        "decision_id": "audit.finding.skill-dream-journey-silver-world-in-dreams",
        "action": "lock",
        "target_vi": PREFERRED,
    }
    assert finding["canonical_resolution"] == {
        "layer": "community",
        "term_id": "skill.dream_journey.silver_world_in_dreams",
        "target_vi": PREFERRED,
    }
    assert active_findings(refreshed) == []


def test_dream_journey_rule_does_not_resolve_other_source_path(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    refreshed = refresh_canonical_resolutions(
        tmp_path,
        {"schema_version": 1, "findings": [_finding(source_path="localize_dict.json")]},
    )
    finding = refreshed["findings"][0]
    assert finding["review_resolution"]["target_vi"] == PREFERRED
    assert finding["canonical_resolution"] is None

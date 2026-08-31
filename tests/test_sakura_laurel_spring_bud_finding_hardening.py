from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import refresh_canonical_resolutions
from scripts.harden_sakura_laurel_spring_bud_finding import SPRING_BUD, harden


def _seed(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    (glossary / "ui_community_terms.json").write_text(json.dumps({"schema_version": 1, "terms": []}), encoding="utf-8")
    (glossary / "terminology_reviews.json").write_text(json.dumps({"schema_version": 1, "decisions": []}), encoding="utf-8")
    (glossary / "term_registry.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "source_bridge_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")


def _finding(prefix: str) -> dict:
    return {
        "finding_id": "cf-test-spring-bud",
        "status": "open",
        "source_zh_cn": "待春之蕾",
        "match_mode": "exact",
        "source_paths": ["text_data_dict.json"],
        "key_exact": [],
        "json_path_prefixes": [[prefix]],
        "suggested_targets_vi": [],
        "canonical_resolution": None,
        "review_resolution": None,
    }


def test_hardener_resolves_sakura_laurel_condition_and_is_idempotent(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False
    community = json.loads((tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8"))
    rule = next(item for item in community["terms"] if item["id"] == SPRING_BUD["id"])
    assert rule["preferred"] == "Flower Bud Awaiting Spring"
    assert rule["json_path_prefixes"] == [["142"]]
    assert rule["match_mode"] == "exact"

    finding = refresh_canonical_resolutions(tmp_path, {"schema_version": 1, "findings": [_finding("142")]})["findings"][0]
    assert finding["review_resolution"]["target_vi"] == "Flower Bud Awaiting Spring"
    assert finding["canonical_resolution"] == {
        "layer": "community",
        "term_id": "condition.sakura_laurel.spring_bud_awaiting_spring",
        "target_vi": "Flower Bud Awaiting Spring",
    }


def test_rule_does_not_resolve_same_text_outside_condition_table(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    finding = refresh_canonical_resolutions(tmp_path, {"schema_version": 1, "findings": [_finding("147")]})["findings"][0]
    assert finding["canonical_resolution"] is None

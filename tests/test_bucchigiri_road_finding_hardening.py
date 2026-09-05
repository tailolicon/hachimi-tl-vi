from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import refresh_canonical_resolutions
from scripts.harden_bucchigiri_road_finding import DECISION, FINDING_ID, RULE, harden


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
    (glossary / "canonical_findings.json").write_text(
        json.dumps({"schema_version": 1, "findings": [_finding("147")]}), encoding="utf-8"
    )


def _finding(prefix: str) -> dict[str, object]:
    return {
        "finding_id": FINDING_ID,
        "status": "open",
        "source_zh_cn": "冠绝之路",
        "match_mode": "exact",
        "source_paths": ["text_data_dict.json"],
        "key_exact": [],
        "json_path_prefixes": [[prefix]],
        "suggested_targets_vi": [],
        "canonical_resolution": None,
        "review_resolution": None,
    }


def test_keep_pushing_ahead_resolves_skill_title_in_category_147(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    community = json.loads(
        (tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8")
    )
    rule = next(item for item in community["terms"] if item["id"] == RULE["id"])
    assert rule["preferred"] == "Keep Pushing Ahead"
    assert rule["json_path_prefixes"] == [["147"]]
    assert rule["match_mode"] == "exact"

    reviews = json.loads(
        (tmp_path / "glossary" / "terminology_reviews.json").read_text(encoding="utf-8")
    )
    decision = next(
        item for item in reviews["decisions"] if item["decision_id"] == DECISION["decision_id"]
    )
    assert decision["target_vi"] == "Keep Pushing Ahead"
    assert decision["ja"] == ["ぶっちぎりロード"]

    ledger = {"schema_version": 1, "findings": [_finding("147")]}
    finding = refresh_canonical_resolutions(tmp_path, ledger)["findings"][0]
    assert finding["review_resolution"] == {
        "decision_id": "audit.finding.skill-mejiro-palmer-keep-pushing-ahead",
        "action": "lock",
        "target_vi": "Keep Pushing Ahead",
    }
    assert finding["canonical_resolution"] == {
        "layer": "community",
        "term_id": "skill.mejiro_palmer.keep_pushing_ahead",
        "target_vi": "Keep Pushing Ahead",
    }


def test_keep_pushing_ahead_does_not_resolve_outside_skill_title_category(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True

    ledger = {"schema_version": 1, "findings": [_finding("16")]}
    finding = refresh_canonical_resolutions(tmp_path, ledger)["findings"][0]
    assert finding["review_resolution"]["target_vi"] == "Keep Pushing Ahead"
    assert finding["canonical_resolution"] is None

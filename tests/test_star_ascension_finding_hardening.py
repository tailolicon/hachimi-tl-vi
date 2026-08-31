from __future__ import annotations

import json
from pathlib import Path

from scripts.apply_terminology_reviews import apply_reviews
from scripts.canonical_findings import refresh_canonical_resolutions
from scripts.harden_star_ascension_finding import REVIEWED_TERM_ID, STAR_ASCENSION, harden


def _seed(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    (glossary / "ui_community_terms.json").write_text(json.dumps({"schema_version": 1, "terms": []}), encoding="utf-8")
    (glossary / "terminology_reviews.json").write_text(json.dumps({"schema_version": 1, "decisions": []}), encoding="utf-8")
    (glossary / "term_registry.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "source_bridge_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")


def _finding(prefix: str) -> dict:
    return {
        "finding_id": "cf-test-star-ascension",
        "status": "open",
        "source_zh_cn": "才能开花",
        "match_mode": "contains",
        "source_paths": ["text_data_dict.json"],
        "key_exact": [],
        "json_path_prefixes": [[prefix]],
        "suggested_targets_vi": [],
        "canonical_resolution": None,
        "review_resolution": None,
    }


def test_hardener_resolves_character_piece_progression_and_is_idempotent(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False
    community = json.loads((tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8"))
    rule = next(item for item in community["terms"] if item["id"] == STAR_ASCENSION["id"])
    assert rule["preferred"] == "Star Ascension"
    assert rule["json_path_prefixes"] == [["114"]]
    assert rule["match_mode"] == "contains"

    finding = refresh_canonical_resolutions(tmp_path, {"schema_version": 1, "findings": [_finding("114")]})["findings"][0]
    assert finding["review_resolution"]["target_vi"] == "Star Ascension"
    assert finding["canonical_resolution"] == {
        "layer": "community",
        "term_id": "system.star_ascension.character_piece_description",
        "target_vi": "Star Ascension",
    }


def test_rule_does_not_resolve_same_phrase_outside_character_piece_category(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    finding = refresh_canonical_resolutions(tmp_path, {"schema_version": 1, "findings": [_finding("147")]})["findings"][0]
    assert finding["canonical_resolution"] is None


def test_hardener_migrates_legacy_talent_bloom_lock_and_decision_before_review_apply(tmp_path: Path) -> None:
    _seed(tmp_path)
    registry_path = tmp_path / "glossary" / "term_registry.json"
    registry_path.write_text(
        json.dumps({
            "terms": [{
                "id": REVIEWED_TERM_ID,
                "category": "progression",
                "zh_cn": ["才能开花"],
                "target_vi": "Talent Bloom",
                "locked": True,
                "review": {"decision_id": "legacy.star-ascension", "source": "test"},
            }]
        }),
        encoding="utf-8",
    )
    reviews_path = tmp_path / "glossary" / "terminology_reviews.json"
    reviews_path.write_text(
        json.dumps({
            "schema_version": 1,
            "decisions": [{
                "decision_id": "audit.finding.talent-bloom-system",
                "source_zh_cn": "才能开花",
                "action": "lock",
                "target_vi": "Talent Bloom",
                "kind": "system_label",
                "category": "progression",
            }],
        }),
        encoding="utf-8",
    )

    assert harden(tmp_path) is True
    migrated = json.loads(registry_path.read_text(encoding="utf-8"))
    legacy = next(term for term in migrated["terms"] if term["id"] == REVIEWED_TERM_ID)
    assert legacy["target_vi"] == "Star Ascension"

    reviews = json.loads(reviews_path.read_text(encoding="utf-8"))
    old_decision = next(item for item in reviews["decisions"] if item["decision_id"] == "audit.finding.talent-bloom-system")
    assert old_decision["target_vi"] == "Star Ascension"
    applied, stats = apply_reviews(migrated, reviews)
    assert stats["locked_existing"] == 2
    reviewed = next(term for term in applied["terms"] if term["id"] == REVIEWED_TERM_ID)
    assert reviewed["target_vi"] == "Star Ascension"
    assert reviewed["source_paths"] == ["text_data_dict.json"]
    assert reviewed["json_path_prefixes"] == [["114"]]
    assert reviewed["match_mode"] == "contains"

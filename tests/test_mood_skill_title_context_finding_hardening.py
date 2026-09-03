from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import refresh_canonical_resolutions
from scripts.harden_mood_skill_title_context_finding import (
    BRIDGE_TERM_ID,
    COMMUNITY_TERM_ID,
    PREFERRED,
    SKILL_DECISION,
    SKILL_TERM_ID,
    SOURCE_ZH,
    harden,
)
from scripts.translation_review_common import community_term_matches, load_community_terms

FINDING_ID = "cf-d91595f0ee324d4a"


def _write(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _seed(root: Path) -> None:
    glossary = root / "glossary"
    glossary.mkdir(parents=True)
    _write(glossary / "ui_community_terms.json", {
        "schema_version": 1,
        "terms": [{
            "id": COMMUNITY_TERM_ID,
            "category": "state",
            "source_aliases": ["やる気", "干劲"],
            "preferred": "Mood",
            "accepted": ["Mood"],
            "forbidden": ["Tinh thần", "Hứng khởi"],
            "require_accepted": True,
        }],
    })
    _write(glossary / "source_bridge_terms.json", {
        "schema_version": 1,
        "terms": [{
            "id": BRIDGE_TERM_ID,
            "category": "state",
            "ja": ["やる気"],
            "zh_cn": ["干劲"],
            "source_aliases": ["干劲"],
            "preferred": "Mood",
            "accepted": ["Mood"],
            "forbidden": ["Tinh thần", "Hứng khởi"],
            "require_accepted": True,
            "match_mode": "contains",
        }],
    })
    _write(glossary / "terminology_reviews.json", {"schema_version": 1, "decisions": []})
    _write(glossary / "term_registry.json", {"schema_version": 1, "terms": []})
    _write(glossary / "skill_name_style.json", {"canonical_examples": []})


def _finding() -> dict:
    return {
        "finding_id": FINDING_ID,
        "status": "open",
        "source_zh_cn": SOURCE_ZH,
        "match_mode": "exact",
        "source_paths": ["text_data_dict.json"],
        "key_exact": [],
        "json_path_prefixes": [],
        "suggested_targets_vi": [],
        "canonical_resolution": None,
        "review_resolution": None,
    }


def test_skill_title_is_locked_and_no_longer_matches_generic_mood(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    terms = load_community_terms(tmp_path)
    title_matches = community_term_matches(
        None,
        SOURCE_ZH,
        "Tràn đầy khí thế",
        terms,
        source_path="text_data_dict.json",
        json_path=["147", "2023102"],
    )
    ids = {match["id"] for match in title_matches}
    assert COMMUNITY_TERM_ID not in ids
    assert SKILL_TERM_ID in ids

    ordinary_mood = community_term_matches(
        None,
        "干劲提升",
        "Mood tăng",
        terms,
        source_path="text_data_dict.json",
        json_path=["1", "1"],
    )
    assert any(match["id"] == COMMUNITY_TERM_ID for match in ordinary_mood)

    bridge = json.loads((tmp_path / "glossary" / "source_bridge_terms.json").read_text(encoding="utf-8"))
    bridge_rule = next(term for term in bridge["terms"] if term["id"] == BRIDGE_TERM_ID)
    assert SOURCE_ZH in bridge_rule["exclude_source_contains"]


def test_skill_title_finding_resolves_to_distinct_skill_canon(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True

    reviews = json.loads((tmp_path / "glossary" / "terminology_reviews.json").read_text(encoding="utf-8"))
    decision = next(item for item in reviews["decisions"] if item["decision_id"] == SKILL_DECISION["decision_id"])
    assert decision["target_vi"] == PREFERRED
    assert decision["ja"] == ["意気込み十分"]

    finding = refresh_canonical_resolutions(
        tmp_path,
        {"schema_version": 1, "findings": [_finding()]},
    )["findings"][0]
    assert finding["review_resolution"] == {
        "decision_id": "audit.finding.skill-ikigomi-jubun",
        "action": "lock",
        "target_vi": PREFERRED,
    }
    assert finding["canonical_resolution"] == {
        "layer": "community",
        "term_id": SKILL_TERM_ID,
        "target_vi": PREFERRED,
    }

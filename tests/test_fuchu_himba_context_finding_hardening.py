from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import refresh_canonical_resolutions
from scripts.harden_fuchu_himba_context_finding import FUCHU_UMA_MUSUME_STAKES, TERM_ID, harden
from scripts.translation_review_common import community_term_matches, load_community_terms


def _seed(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir(parents=True)
    (glossary / "ui_community_terms.json").write_text(json.dumps({"terms": [{
        "id": TERM_ID,
        "source_aliases": ["赛马娘"],
        "preferred": "Mã Nương",
        "accepted": ["Mã Nương"],
        "forbidden": ["Uma Musume"],
        "require_accepted": True,
    }]}, ensure_ascii=False), encoding="utf-8")
    (glossary / "terminology_reviews.json").write_text(json.dumps({"schema_version": 1, "decisions": []}), encoding="utf-8")
    (glossary / "term_registry.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "source_bridge_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")


def _finding(prefix: str = "131") -> dict:
    return {
        "finding_id": "cf-test-fuchu-proper-name",
        "status": "open",
        "source_zh_cn": "府中赛马娘锦标",
        "match_mode": "contains",
        "source_paths": ["text_data_dict.json"],
        "key_exact": [],
        "json_path_prefixes": [[prefix]],
        "suggested_targets_vi": ["Fuchu Himba Stakes"],
        "canonical_resolution": None,
        "review_resolution": None,
    }


def test_generic_umamusume_does_not_match_fuchu_uma_musume_stakes(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False
    terms = load_community_terms(tmp_path)
    generic = community_term_matches(None, "赛马娘", "Mã Nương", terms, source_path="text_data_dict.json", json_path=["1", "1"])
    race = community_term_matches(None, "取得府中赛马娘锦标的胜利", "Chiến thắng Fuchu Uma Musume Stakes", terms, source_path="text_data_dict.json", json_path=["131", "314"])
    assert generic[0]["id"] == TERM_ID
    assert not any(match["id"] == TERM_ID for match in race)
    proper = next(match for match in race if match["id"] == FUCHU_UMA_MUSUME_STAKES["id"])
    assert proper["accepted_present"] is True
    assert proper["forbidden_present"] is False


def test_proper_name_finding_resolves_to_in_game_name(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    resolved = refresh_canonical_resolutions(
        tmp_path,
        {"schema_version": 1, "findings": [_finding()]},
    )["findings"][0]
    assert resolved["review_resolution"]["target_vi"] == "Fuchu Uma Musume Stakes"
    assert resolved["canonical_resolution"] == {
        "layer": "community",
        "term_id": "race.fuchu_uma_musume_stakes.text131",
        "target_vi": "Fuchu Uma Musume Stakes",
    }


def test_proper_name_rule_does_not_escape_category_131(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    resolved = refresh_canonical_resolutions(
        tmp_path,
        {"schema_version": 1, "findings": [_finding("128")]},
    )["findings"][0]
    assert resolved["canonical_resolution"] is None

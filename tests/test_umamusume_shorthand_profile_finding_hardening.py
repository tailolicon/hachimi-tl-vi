from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import refresh_canonical_resolutions
from scripts.harden_umamusume_shorthand_profile_finding import PREFERRED, SOURCE_ZH, TERM_ID, harden
from scripts.translation_review_common import community_term_matches, load_community_terms

FINDING_ID = "cf-cd337bc7f688a0d4"


def _write(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _seed(root: Path) -> None:
    glossary = root / "glossary"
    glossary.mkdir(parents=True)
    _write(glossary / "ui_community_terms.json", {
        "schema_version": 1,
        "terms": [{
            "id": "common.world.umamusume",
            "category": "world_term",
            "source_aliases": ["ウマ娘", "赛马娘"],
            "preferred": PREFERRED,
            "accepted": [PREFERRED],
            "forbidden": ["Uma Musume"],
            "require_accepted": True,
        }],
    })
    _write(glossary / "term_registry.json", {"schema_version": 1, "terms": []})
    _write(glossary / "terminology_reviews.json", {"schema_version": 1, "decisions": []})
    _write(glossary / "skill_name_style.json", {"canonical_examples": []})


def _finding() -> dict:
    return {
        "finding_id": FINDING_ID,
        "status": "open",
        "source_zh_cn": SOURCE_ZH,
        "match_mode": "contains",
        "source_paths": ["text_data_dict.json"],
        "key_exact": [],
        "json_path_prefixes": [["144"]],
        "suggested_targets_vi": [PREFERRED],
        "canonical_resolution": None,
        "review_resolution": None,
    }


def test_profile_shorthand_is_scoped_to_category_144(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False
    terms = load_community_terms(tmp_path)

    profile = community_term_matches(
        None,
        "不受极限束缚的暴走赛马娘！",
        "Mã Nương bạo tẩu không bị giới hạn trói buộc!",
        terms,
        source_path="text_data_dict.json",
        json_path=["144", "1066"],
    )
    assert any(match["id"] == TERM_ID for match in profile)

    outside = community_term_matches(
        None,
        "赛马娘",
        PREFERRED,
        terms,
        source_path="text_data_dict.json",
        json_path=["47", "1"],
    )
    assert not any(match["id"] == TERM_ID for match in outside)


def test_worker_finding_resolves_through_scoped_community_rule(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    finding = refresh_canonical_resolutions(
        tmp_path,
        {"schema_version": 1, "findings": [_finding()]},
    )["findings"][0]
    assert finding["canonical_resolution"] == {
        "layer": "community",
        "term_id": TERM_ID,
        "target_vi": PREFERRED,
    }

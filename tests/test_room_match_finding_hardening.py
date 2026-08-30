from __future__ import annotations

import json
from pathlib import Path

from scripts.harden_room_match_finding import ROOM_MATCH, harden
from scripts.translation_review_common import community_term_matches, load_community_terms


def _write_terms(root: Path) -> None:
    glossary = root / "glossary"
    glossary.mkdir(parents=True)
    (glossary / "ui_community_terms.json").write_text('{"terms": []}\n', encoding="utf-8")


def test_room_match_hardening_is_scoped_and_idempotent(tmp_path: Path) -> None:
    _write_terms(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    terms = load_community_terms(tmp_path)
    matched = community_term_matches(
        "RoomMatch0001",
        "房间竞赛",
        "Đua phòng",
        terms,
        source_path="localize_dict.json",
        json_path=["RoomMatch0001"],
    )
    unrelated = community_term_matches(
        "Other0001",
        "房间竞赛",
        "Đua phòng",
        terms,
        source_path="localize_dict.json",
        json_path=["Other0001"],
    )
    assert matched[0]["id"] == ROOM_MATCH["id"]
    assert matched[0]["preferred"] == "Room Match"
    assert matched[0]["forbidden_present"] is True
    assert unrelated == []

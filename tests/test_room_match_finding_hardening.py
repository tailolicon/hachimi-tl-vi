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
    replay = community_term_matches(
        "RoomMatch400029",
        "可以在参赛赛马娘、比赛条件不变的情况下\n再次举办房间竞赛。\n要在同条件下举办房间竞赛吗？",
        "Có thể tổ chức lại Đua Phòng mà không thay đổi Mã Nương tham gia và điều kiện cuộc đua.",
        terms,
        source_path="localize_dict.json",
        json_path=["RoomMatch400029"],
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
    assert replay[0]["id"] == ROOM_MATCH["id"]
    assert replay[0]["preferred"] == "Room Match"
    assert replay[0]["forbidden_present"] is True
    assert unrelated == []

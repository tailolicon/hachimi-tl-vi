from __future__ import annotations

import json
from pathlib import Path

from scripts.harden_resources_gacha_shop_canon import harden
from scripts.translation_review_common import source_bridge_term_matches


def _seed(root: Path) -> list[dict]:
    path = root / "glossary" / "source_bridge_terms.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"schema_version": 1, "terms": []}, ensure_ascii=False) + "\n", encoding="utf-8")
    harden(root)
    return json.loads(path.read_text(encoding="utf-8"))["terms"]


def test_goddess_statues_match_gacha_resource_not_story_prose(tmp_path: Path) -> None:
    terms = _seed(tmp_path)
    gacha = source_bridge_term_matches(
        "兑换育成赛马娘后获得了女神像",
        "Sau khi đổi Uma Musume, nhận Goddess Statues",
        terms,
        key="Gacha0067",
        source_path="localize_dict.json",
        json_path=["Gacha0067"],
    )
    old = source_bridge_term_matches(
        "兑换育成赛马娘后获得了女神像",
        "Sau khi đổi Uma Musume, nhận Tượng Nữ thần",
        terms,
        key="Gacha0067",
        source_path="localize_dict.json",
        json_path=["Gacha0067"],
    )
    prose = source_bridge_term_matches(
        "大厅中央摆着一尊女神像。",
        "Giữa đại sảnh có một tượng nữ thần.",
        terms,
        key=None,
        source_path="text_data_dict.json",
        json_path=["181", "2001"],
    )
    assert [item["id"] for item in gacha] == ["resource.goddess_statue"]
    assert gacha[0]["accepted_present"] is True
    assert [item["id"] for item in old] == ["resource.goddess_statue"]
    assert old[0]["forbidden_present"] is True
    assert prose == []


def test_club_points_are_exact_key_scoped_until_more_context_is_proven(tmp_path: Path) -> None:
    terms = _seed(tmp_path)
    observed = source_bridge_term_matches(
        "社团点数兑换",
        "Đổi Club Points",
        terms,
        key="StoryEvent4080030",
        source_path="localize_dict.json",
        json_path=["StoryEvent4080030"],
    )
    old = source_bridge_term_matches(
        "社团点数兑换",
        "Đổi điểm câu lạc bộ",
        terms,
        key="StoryEvent4080030",
        source_path="localize_dict.json",
        json_path=["StoryEvent4080030"],
    )
    unrelated = source_bridge_term_matches(
        "社团点数相关说明",
        "Giải thích về điểm câu lạc bộ",
        terms,
        key="StoryEvent9999999",
        source_path="localize_dict.json",
        json_path=["StoryEvent9999999"],
    )
    assert [item["id"] for item in observed] == ["currency.club_points"]
    assert observed[0]["accepted_present"] is True
    assert [item["id"] for item in old] == ["currency.club_points"]
    assert old[0]["forbidden_present"] is True
    assert unrelated == []

from __future__ import annotations

import json
from pathlib import Path

from scripts.harden_character_training_ui_canon import harden
from scripts.translation_review_common import (
    community_term_matches,
    load_community_terms,
    load_locked_terms,
    locked_term_matches,
)


def _seed(tmp_path: Path) -> Path:
    glossary = tmp_path / "glossary"
    glossary.mkdir(parents=True)
    (glossary / "term_registry.json").write_text(
        json.dumps({"schema_version": 1, "terms": []}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return tmp_path


def _seed_with_world_term(tmp_path: Path) -> Path:
    root = _seed(tmp_path)
    (root / "glossary" / "ui_community_terms.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "terms": [
                    {
                        "id": "common.world.umamusume",
                        "source_aliases": ["赛马娘"],
                        "preferred": "Mã Nương",
                        "accepted": ["Mã Nương"],
                        "forbidden": ["Uma Musume"],
                        "require_accepted": True,
                    }
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    harden(root)
    return root


def _ids(matches: list[dict[str, object]]) -> set[str]:
    return {str(item.get("id")) for item in matches}


def test_career_mode_is_required_at_proven_system_keys(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    harden(root)
    locked = load_locked_terms(root)
    samples = (
        ("SingleMode0039", "育成结束前", "Trước khi Career kết thúc"),
        ("SingleMode0526", "开始育成时将消耗金币", "Bắt đầu Career sẽ tốn Coin"),
        ("SingleMode0534", "育成难易度选择", "Chọn độ khó Career"),
        ("SingleMode0538", "再次育成", "Career lại"),
        ("SingleMode194016", "育成结果", "Kết quả Career"),
        ("SingleMode194020", "育成模式", "Chế độ Career"),
        (
            "SingleModeScenarioTeamRace0033",
            "还未进行过此剧本的育成",
            "Chưa bắt đầu Career trong Scenario này",
        ),
    )
    for key, source, target in samples:
        matches = locked_term_matches(
            source,
            target,
            locked,
            key=key,
            source_path="localize_dict.json",
            json_path=[key],
        )
        assert "career.ui.mode" in _ids(matches)


def test_trainee_compound_has_its_own_player_facing_term(tmp_path: Path) -> None:
    root = _seed_with_world_term(tmp_path)
    locked = load_locked_terms(root)
    community = load_community_terms(root)
    samples = (
        ("SingleMode0038", "选择育成赛马娘", "Chọn Trainee"),
        ("SingleModeScenarioMecha194090", "育成\n赛马娘", "Trainee"),
    )
    for key, source, target in samples:
        locked_matches = locked_term_matches(
            source,
            target,
            locked,
            key=key,
            source_path="localize_dict.json",
            json_path=[key],
        )
        assert "career.ui.trainee" in _ids(locked_matches)
        assert "career.ui.mode" not in _ids(locked_matches)
        community_matches = community_term_matches(
            key,
            source,
            target,
            community,
            source_path="localize_dict.json",
            json_path=[key],
        )
        assert "common.world.umamusume" not in _ids(community_matches)


def test_generic_umamusume_still_uses_world_term_after_trainee_exclusion(tmp_path: Path) -> None:
    root = _seed_with_world_term(tmp_path)
    community = load_community_terms(root)
    matches = community_term_matches(
        "SingleModeScenarioMecha194045",
        "机械赛马娘详情",
        "Chi tiết Mã Nương Mecha",
        community,
        source_path="localize_dict.json",
        json_path=["SingleModeScenarioMecha194045"],
    )
    assert "common.world.umamusume" in _ids(matches)


def test_career_mode_rule_does_not_match_story_training_prose(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    harden(root)
    locked = load_locked_terms(root)
    matches = locked_term_matches(
        "为了育成后辈，她每天都认真指导",
        "Để dìu dắt đàn em, cô ấy ngày nào cũng chỉ dẫn tận tình",
        locked,
        source_path="text_data_dict.json",
        json_path=["163", "1"],
    )
    assert "career.ui.mode" not in _ids(matches)

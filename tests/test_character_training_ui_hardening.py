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


REPO_ROOT = Path(__file__).resolve().parents[1]


def _by_id(matches: list[dict[str, object]], term_id: str) -> dict[str, object]:
    return next(item for item in matches if item["id"] == term_id)


def _ids(matches: list[dict[str, object]]) -> set[str]:
    return {str(item.get("id")) for item in matches}


def _seed_hardener(tmp_path: Path) -> Path:
    glossary = tmp_path / "glossary"
    glossary.mkdir(parents=True)
    (glossary / "term_registry.json").write_text(
        json.dumps({"schema_version": 1, "terms": []}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    harden(tmp_path)
    return tmp_path


def test_trainer_role_accepts_player_facing_term_in_account_ui() -> None:
    community = load_community_terms(REPO_ROOT)
    matches = community_term_matches(
        "AccoutDataLink0017",
        "输入训练员ID和连携密码",
        "Enter Trainer ID and link password",
        community,
        source_path="localize_dict.json",
        json_path=["AccoutDataLink0017"],
    )
    record = _by_id(matches, "common.trainer")
    assert record["accepted_present"] is True
    assert record["forbidden_present"] is False


def test_trainer_role_rejects_historical_vietnamese_calque() -> None:
    community = load_community_terms(REPO_ROOT)
    matches = community_term_matches(
        "AccoutDataLink0017",
        "输入训练员ID和连携密码",
        "Nhập ID Huấn luyện viên và mật khẩu liên kết",
        community,
        source_path="localize_dict.json",
        json_path=["AccoutDataLink0017"],
    )
    record = _by_id(matches, "common.trainer")
    assert record["accepted_present"] is False
    assert record["forbidden_present"] is True


def test_trainer_role_matches_other_repeated_account_ui_contexts() -> None:
    community = load_community_terms(REPO_ROOT)
    samples = [
        ("AccoutDataLink0021", "请输入训练员ID"),
        ("AccoutDataLink0053", "登录的{0}账号上\n存在已经连携的训练员ID"),
        ("AccoutDataLink0066", "训练员信息输入"),
        ("AccoutDataLink0103", "请输入训练员ID和密码"),
    ]
    for key, source in samples:
        matches = community_term_matches(
            key,
            source,
            "Trainer",
            community,
            source_path="localize_dict.json",
            json_path=[key],
        )
        record = _by_id(matches, "common.trainer")
        assert record["accepted_present"] is True


def test_aptitude_label_accepts_established_player_term() -> None:
    community = load_community_terms(REPO_ROOT)
    matches = community_term_matches(
        None,
        "适性",
        "Aptitude",
        community,
        source_path="text_data_dict.json",
        json_path=["example"],
    )
    record = _by_id(matches, "common.aptitude")
    assert record["accepted_present"] is True
    assert record["forbidden_present"] is False


def test_singlemode_aptitude_composes_with_scoped_surface_canon() -> None:
    community = load_community_terms(REPO_ROOT)
    matches = community_term_matches(
        "SingleMode0078",
        "草地适性",
        "Turf Aptitude",
        community,
        source_path="localize_dict.json",
        json_path=["SingleMode0078"],
    )
    ids = _ids(matches)
    assert "common.surface.turf.aptitude" in ids
    assert "common.aptitude" in ids
    assert _by_id(matches, "common.surface.turf.aptitude")["accepted_present"] is True
    assert _by_id(matches, "common.aptitude")["accepted_present"] is True


def test_career_class_rules_do_not_overmatch_story_prose() -> None:
    locked = load_locked_terms(REPO_ROOT)
    matches = locked_term_matches(
        "在新马级比赛中表现出色的希望之星",
        "Những ngôi sao nổi bật trong các cuộc đua tân mã",
        locked,
        source_path="text_data_dict.json",
        json_path=["163", "1"],
    )
    assert not any(term_id.startswith("race.class.") for term_id in _ids(matches))


def test_scoped_goal_race_turn_and_rating_labels(tmp_path: Path) -> None:
    root = _seed_hardener(tmp_path)
    locked = load_locked_terms(root)
    cases = (
        ("SingleMode585006", "目标比赛", "Goal Race", "career.ui.goal_race"),
        ("SingleMode0537", "回合", "Lượt", "career.ui.turn"),
        ("SingleModeScenarioBreeders508058", "评价", "Rating", "career.ui.rating"),
        ("SingleModeScenarioBreeders508040", "队伍评价", "Team Rating", "career.ui.team_rating"),
    )
    for key, source, target, expected in cases:
        matches = locked_term_matches(
            source,
            target,
            locked,
            key=key,
            source_path="localize_dict.json",
            json_path=[key],
        )
        assert expected in _ids(matches)


def test_scenario_is_player_facing_only_at_proven_career_keys(tmp_path: Path) -> None:
    root = _seed_hardener(tmp_path)
    locked = load_locked_terms(root)
    cases = (
        ("SingleModeScenarioTeamRace0033", "还未进行过此剧本的育成", "Chưa bắt đầu Career trong Scenario này"),
        ("SingleModeScenarioTeamRace0037", "剧本\n关联", "Scenario\nliên quan"),
    )
    for key, source, target in cases:
        matches = locked_term_matches(
            source,
            target,
            locked,
            key=key,
            source_path="localize_dict.json",
            json_path=[key],
        )
        assert "career.ui.scenario" in _ids(matches)

    story = locked_term_matches(
        "这个剧本的结尾让我很感动",
        "Đoạn kết kịch bản này làm tôi rất xúc động",
        locked,
        source_path="text_data_dict.json",
        json_path=["163", "1"],
    )
    assert "career.ui.scenario" not in _ids(story)


def test_track_is_scoped_to_proven_room_match_ui(tmp_path: Path) -> None:
    root = _seed_hardener(tmp_path)
    locked = load_locked_terms(root)
    matches = locked_term_matches(
        "请设定要举办的赛道和条件",
        "Hãy thiết lập Track và điều kiện tổ chức",
        locked,
        key="RoomMatch600128",
        source_path="localize_dict.json",
        json_path=["RoomMatch600128"],
    )
    assert "race.ui.track.room_match" in _ids(matches)
    prose = locked_term_matches(
        "沿着山间赛道散步",
        "Đi dạo dọc con đường trên núi",
        locked,
        source_path="text_data_dict.json",
        json_path=["163", "1"],
    )
    assert "race.ui.track.room_match" not in _ids(prose)


def test_generic_world_umamusume_uses_ma_nuong_but_brand_is_excluded() -> None:
    community = load_community_terms(REPO_ROOT)
    generic = community_term_matches(
        "SingleModeScenarioMecha194045",
        "机械赛马娘详情",
        "Chi tiết Mã Nương Mecha",
        community,
        source_path="localize_dict.json",
        json_path=["SingleModeScenarioMecha194045"],
    )
    record = _by_id(generic, "common.world.umamusume")
    assert record["accepted_present"] is True
    assert record["forbidden_present"] is False

    brand = community_term_matches(
        "Title",
        "赛马娘 Pretty Derby",
        "Umamusume: Pretty Derby",
        community,
        source_path="localize_dict.json",
        json_path=["Title"],
    )
    assert "common.world.umamusume" not in _ids(brand)


def test_scoped_career_labels_do_not_match_prose_or_wrong_keys(tmp_path: Path) -> None:
    root = _seed_hardener(tmp_path)
    locked = load_locked_terms(root)
    wrong_key = locked_term_matches(
        "目标比赛",
        "Goal Race",
        locked,
        key="Story0001",
        source_path="localize_dict.json",
        json_path=["Story0001"],
    )
    prose = locked_term_matches(
        "这场比赛是她一直以来的目标",
        "Cuộc đua này luôn là mục tiêu của cô ấy",
        locked,
        source_path="text_data_dict.json",
        json_path=["163", "1"],
    )
    assert "career.ui.goal_race" not in _ids(wrong_key)
    assert not any(term_id.startswith("career.ui.") for term_id in _ids(prose))


def test_character_ui_hardener_is_idempotent(tmp_path: Path) -> None:
    root = _seed_hardener(tmp_path)
    before = (root / "glossary" / "term_registry.json").read_text(encoding="utf-8")
    harden(root)
    after = (root / "glossary" / "term_registry.json").read_text(encoding="utf-8")
    assert after == before


def test_scenario_and_condition_keep_unsafe_global_aliases_disabled() -> None:
    community = load_community_terms(REPO_ROOT)
    scenario = next(item for item in community if item.get("id") == "common.scenario")
    condition = next(item for item in community if item.get("id") == "common.condition")
    assert scenario.get("source_aliases") == []
    assert scenario.get("preferred") == "Scenario"
    assert condition.get("source_aliases") == []
    assert condition.get("preferred") == "Condition"

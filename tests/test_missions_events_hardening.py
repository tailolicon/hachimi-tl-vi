from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.harden_missions_events_canon import harden
from scripts.translation_review_common import community_term_matches, load_community_terms, load_locked_terms, locked_term_matches


def _write(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _seed(tmp_path: Path) -> Path:
    glossary = tmp_path / "glossary"
    _write(glossary / "term_registry.json", {"terms": []})
    _write(glossary / "ui_community_terms.json", {"terms": []})
    harden(tmp_path)
    return tmp_path


def _ids(items: list[dict[str, object]]) -> set[str]:
    return {str(item.get("id")) for item in items}


@pytest.mark.parametrize("item_id", ["12", "13"])
def test_login_bonus_is_enforced_at_verified_system_labels(tmp_path: Path, item_id: str) -> None:
    root = _seed(tmp_path)
    locked = load_locked_terms(root)
    community = load_community_terms(root)
    source = "登录奖励"
    target = "Login Bonus"

    assert f"system.login_bonus.text171_{item_id}" in _ids(
        locked_term_matches(source, target, locked, source_path="text_data_dict.json", json_path=["171", item_id])
    )
    matches = community_term_matches(None, source, target, community, source_path="text_data_dict.json", json_path=["171", item_id])
    record = next(item for item in matches if item["id"] == f"common.login_bonus.text171_{item_id}")
    assert record["accepted_present"] is True
    assert record["forbidden_present"] is False


@pytest.mark.parametrize("item_id", ["12", "13"])
def test_login_bonus_rejects_old_vietnamese_calque(tmp_path: Path, item_id: str) -> None:
    root = _seed(tmp_path)
    community = load_community_terms(root)
    matches = community_term_matches(
        None, "登录奖励", "Phần thưởng đăng nhập", community,
        source_path="text_data_dict.json", json_path=["171", item_id],
    )
    record = next(item for item in matches if item["id"] == f"common.login_bonus.text171_{item_id}")
    assert record["accepted_present"] is False
    assert record["forbidden_present"] is True


@pytest.mark.parametrize(
    ("rid", "source", "target", "key"),
    [
        ("mission.home", "任务", "Nhiệm vụ", "Home0011"),
        ("event_mission.story", "活动任务", "Nhiệm vụ sự kiện", "StoryEvent0044"),
        ("event_mission.multiline", "活动\n任务", "Nhiệm vụ\nsự kiện", "StoryEvent0024"),
        ("event_mission.multiline", "活动\n任务", "Nhiệm vụ\nsự kiện", "CollectEvent508007"),
        ("event_points.story", "活动点数", "Điểm sự kiện", "StoryEvent0022"),
        ("reward_claim.present", "领取", "Nhận", "Present0003"),
        ("reward_claim.story_event", "领取奖励", "Nhận phần thưởng", "StoryEvent0054"),
        ("reward_claim.claimed", "已领取", "Đã nhận", "Present0016"),
        ("reward_claim.unclaimed", "未领取", "Chưa nhận", "Present0009"),
        ("reward_claim.deadline", "领取期限", "Hạn nhận", "TransferEvent0003"),
        ("reward_claim.deadline", "领取期限", "Hạn nhận", "Present0040"),
        ("reward.obtain", "获得报酬", "Nhận thưởng", "Champions0024"),
        ("reward.obtain", "获得报酬", "Nhận thưởng", "Champions0030"),
        ("reward.obtain", "获得报酬", "Nhận thưởng", "Champions0076"),
        ("reward.obtain", "获得报酬", "Nhận thưởng", "Common0164"),
        ("reward.list", "报酬一览", "Danh sách phần thưởng", "Race0260"),
        ("reward.list", "报酬一览", "Danh sách phần thưởng", "TrainingChallenge4080016"),
        ("event_reward.personal", "活动个人奖励", "Thưởng cá nhân", "FanRaid424003"),
        ("event_reward.personal", "活动个人奖励", "Thưởng cá nhân", "CollectEvent508002"),
        ("event_reward.activity", "活动奖励", "Thưởng sự kiện", "FanRaid400102"),
        ("event_reward.group", "活动全体奖励", "Thưởng chung", "FanRaid424002"),
        ("event_reward.group", "活动全体奖励", "Thưởng chung", "CollectEvent508001"),
    ],
)
def test_verified_localize_labels_match_only_their_scoped_keys(
    tmp_path: Path, rid: str, source: str, target: str, key: str
) -> None:
    root = _seed(tmp_path)
    locked = load_locked_terms(root)
    community = load_community_terms(root)

    assert f"system.{rid}" in _ids(
        locked_term_matches(source, target, locked, source_path="localize_dict.json", json_path=[key])
    )
    matches = community_term_matches(None, source, target, community, source_path="localize_dict.json", json_path=[key])
    record = next(item for item in matches if item["id"] == f"common.{rid}")
    assert record["accepted_present"] is True

    assert f"system.{rid}" not in _ids(
        locked_term_matches(source, target, locked, source_path="localize_dict.json", json_path=["WrongKey999"])
    )


def test_mission_like_skill_name_and_prose_are_not_canonicalized(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    locked = load_locked_terms(root)
    community = load_community_terms(root)

    for source, target, path, json_path in [
        ("任务：凯旋", "Nhiệm vụ: Khải hoàn", "text_data_dict.json", ["147", "10830101"]),
        ("海外诞生，沉默寡言的任务执行者", "Sinh ra ở hải ngoại, người thi hành nhiệm vụ ít lời", "text_data_dict.json", ["144", "1083"]),
        ("活动期间外，不能挑战活动任务", "Ngoài thời gian sự kiện, không thể thực hiện nhiệm vụ sự kiện", "localize_dict.json", ["CollectEvent508017"]),
    ]:
        assert not (_ids(locked_term_matches(source, target, locked, source_path=path, json_path=json_path)) & {
            "system.mission.home", "system.event_mission.story", "system.event_mission.multiline", "system.event_points.story",
        })
        assert not [
            item for item in community_term_matches(None, source, target, community, source_path=path, json_path=json_path)
            if str(item.get("id", "")).startswith(("common.mission.", "common.event_mission.", "common.event_points."))
        ]


def test_reward_claim_prose_and_full_deadline_sentences_are_not_canonicalized(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    locked = load_locked_terms(root)
    community = load_community_terms(root)
    reward_ids = {
        "system.reward_claim.present", "system.reward_claim.story_event", "system.reward_claim.claimed",
        "system.reward_claim.unclaimed", "system.reward_claim.deadline",
    }
    for source, target, key in [
        ("为了领取奖励，是否启动浏览器访问官方网站？", "Để nhận phần thưởng, bạn có muốn mở trình duyệt truy cập trang chính thức?", "Heroes467005"),
        ("领取期限已结束", "Đã hết hạn nhận", "TransferEvent0024"),
        ("收到活动任务中未领取的报酬", "Đã nhận phần thưởng chưa nhận từ nhiệm vụ sự kiện", "CollectEvent508019"),
        ("活动奖励领取时间已结束", "Đã hết thời gian nhận thưởng sự kiện", "FanRaid400117"),
        ("获得报酬后可继续挑战", "Sau khi nhận thưởng có thể tiếp tục thử thách", "Champions0999"),
    ]:
        assert not (_ids(locked_term_matches(source, target, locked, source_path="localize_dict.json", json_path=[key])) & reward_ids)
        assert not [
            item for item in community_term_matches(None, source, target, community, source_path="localize_dict.json", json_path=[key])
            if str(item.get("id", "")).startswith("common.reward_claim.")
        ]


def test_login_reward_prose_outside_verified_path_does_not_match(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    locked = load_locked_terms(root)
    community = load_community_terms(root)
    source = "登录后可以领取奖励"
    target = "Đăng nhập xong có thể nhận thưởng"

    assert not (_ids(locked_term_matches(source, target, locked, source_path="story.json", json_path=["1"])) & {
        "system.login_bonus.text171_12", "system.login_bonus.text171_13",
    })
    assert community_term_matches(None, source, target, community, source_path="story.json", json_path=["1"]) == []


def test_same_alias_at_wrong_text_data_path_does_not_match(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    locked = load_locked_terms(root)
    community = load_community_terms(root)

    assert not (_ids(locked_term_matches(
        "登录奖励", "Phần thưởng đăng nhập", locked,
        source_path="text_data_dict.json", json_path=["171", "99"],
    )) & {"system.login_bonus.text171_12", "system.login_bonus.text171_13"})
    assert community_term_matches(
        None, "登录奖励", "Phần thưởng đăng nhập", community,
        source_path="text_data_dict.json", json_path=["171", "99"],
    ) == []


def test_hardener_is_idempotent(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    before = (
        (root / "glossary/term_registry.json").read_text(encoding="utf-8"),
        (root / "glossary/ui_community_terms.json").read_text(encoding="utf-8"),
    )
    harden(root)
    after = (
        (root / "glossary/term_registry.json").read_text(encoding="utf-8"),
        (root / "glossary/ui_community_terms.json").read_text(encoding="utf-8"),
    )
    assert before == after

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]


def _load(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _upsert(items: list[dict[str, Any]], record: dict[str, Any]) -> None:
    rid = str(record["id"])
    for index, item in enumerate(items):
        if isinstance(item, dict) and str(item.get("id", "")) == rid:
            merged = dict(item)
            merged.update(record)
            items[index] = merged
            return
    items.append(dict(record))


def _login_bonus_record(item_id: str) -> dict[str, Any]:
    return {
        "id": f"system.login_bonus.text171_{item_id}",
        "category": "event_system",
        "ja": ["ログインボーナス"],
        "zh_cn": ["登录奖励"],
        "target_vi": "Login Bonus",
        "locked": True,
        "source_paths": ["text_data_dict.json"],
        "json_path_prefixes": [["171", item_id]],
        "match_mode": "exact",
        "invalidation_scope": "item",
        "note": (
            f"Verified repeated player-facing Login Bonus label at text_data category 171 item {item_id}. "
            "Keep the official system label in English; do not generalize ordinary login/reward prose."
        ),
    }


def _login_bonus_community_record(item_id: str) -> dict[str, Any]:
    return {
        "id": f"common.login_bonus.text171_{item_id}",
        "source_aliases": ["登录奖励"],
        "preferred": "Login Bonus",
        "accepted": ["Login Bonus"],
        "compact": [],
        "forbidden": ["Phần thưởng đăng nhập", "phần thưởng đăng nhập"],
        "require_accepted": True,
        "source_paths": ["text_data_dict.json"],
        "json_path_prefixes": [["171", item_id]],
        "match_mode": "exact",
        "invalidation_scope": "item",
        "basis": (
            f"The exact text_data 171/{item_id} system label is Login Bonus. The path guard prevents matching "
            "generic prose that merely mentions logging in or receiving a reward."
        ),
    }


def _localize_system_record(
    rid: str,
    source: str,
    target: str,
    keys: list[str],
    note: str,
) -> dict[str, Any]:
    return {
        "id": rid,
        "category": "event_system",
        "zh_cn": [source],
        "target_vi": target,
        "locked": True,
        "source_paths": ["localize_dict.json"],
        "json_path_prefixes": [[key] for key in keys],
        "match_mode": "exact",
        "invalidation_scope": "item",
        "note": note,
    }


def _localize_community_record(
    rid: str,
    source: str,
    target: str,
    keys: list[str],
    basis: str,
) -> dict[str, Any]:
    return {
        "id": rid,
        "source_aliases": [source],
        "preferred": target,
        "accepted": [target],
        "compact": [],
        "forbidden": [],
        "require_accepted": True,
        "source_paths": ["localize_dict.json"],
        "json_path_prefixes": [[key] for key in keys],
        "match_mode": "exact",
        "invalidation_scope": "item",
        "basis": basis,
    }


LOCALIZE_LABELS: tuple[tuple[str, str, str, list[str], str], ...] = (
    (
        "mission.home", "任务", "Nhiệm vụ", ["Home0011"],
        "Home0011 is the standalone player-facing Missions navigation label; scope by exact key so skill names and prose containing 任务 remain natural.",
    ),
    (
        "event_mission.story", "活动任务", "Nhiệm vụ sự kiện", ["StoryEvent0044"],
        "StoryEvent0044 is the standalone Event Mission label; keep ordinary sentences mentioning event missions outside the rule.",
    ),
    (
        "event_mission.multiline", "活动\n任务", "Nhiệm vụ\nsự kiện", ["StoryEvent0024", "CollectEvent508007"],
        "The same two-line Event Mission navigation label is repeated at StoryEvent0024 and CollectEvent508007; preserve the deliberate line break and key scope.",
    ),
    (
        "event_points.story", "活动点数", "Điểm sự kiện", ["StoryEvent0022"],
        "StoryEvent0022 is the standalone Event Points label; exact-key scope prevents prose about earning or accumulating points from becoming a fixed label.",
    ),
    (
        "reward_claim.present", "领取", "Nhận", ["Present0003"],
        "Present0003 is the standalone claim action in the Present Box. Exact-key scope avoids forcing generic 领取 prose into a button label.",
    ),
    (
        "reward_claim.story_event", "领取奖励", "Nhận phần thưởng", ["StoryEvent0054"],
        "StoryEvent0054 is the standalone Story Event reward-claim action; keep explanatory reward sentences outside the rule.",
    ),
    (
        "reward_claim.claimed", "已领取", "Đã nhận", ["Present0016"],
        "Present0016 is the Present Box claimed-status label, scoped to the exact UI key.",
    ),
    (
        "reward_claim.unclaimed", "未领取", "Chưa nhận", ["Present0009"],
        "Present0009 is the Present Box unclaimed-status label, scoped to the exact UI key.",
    ),
    (
        "reward_claim.deadline", "领取期限", "Hạn nhận", ["TransferEvent0003", "Present0040"],
        "TransferEvent0003 and Present0040 use the same compact claim-deadline label; exact keys prevent overmatching full deadline sentences.",
    ),
    (
        "reward.obtain", "获得报酬", "Nhận thưởng", ["Champions0024", "Champions0030", "Champions0076", "Common0164"],
        "Four standalone UI occurrences use the same receive-reward label; exact-key scope excludes explanatory reward sentences.",
    ),
    (
        "reward.list", "报酬一览", "Danh sách phần thưởng", ["Race0260", "TrainingChallenge4080016"],
        "Race0260 and TrainingChallenge4080016 use the same standalone reward-list heading.",
    ),
    (
        "event_reward.personal", "活动个人奖励", "Thưởng cá nhân", ["FanRaid424003", "CollectEvent508002"],
        "Two event-system screens use the same compact personal-reward heading; keep long event-reward prose outside the rule.",
    ),
    (
        "event_reward.activity", "活动奖励", "Thưởng sự kiện", ["FanRaid400102"],
        "FanRaid400102 is a standalone Event Rewards heading, protected by exact-key scope.",
    ),
    (
        "event_reward.group", "活动全体奖励", "Thưởng chung", ["FanRaid424002", "CollectEvent508001"],
        "Two event-system screens use the same compact group-reward heading; normalize the conflicting verbose variant while retaining exact-key scope.",
    ),
)


def harden(repo_root: Path = REPO_ROOT) -> None:
    registry_path = repo_root / "glossary/term_registry.json"
    registry = _load(registry_path, {"terms": []})
    terms = registry.setdefault("terms", [])

    for item_id in ("12", "13"):
        _upsert(terms, _login_bonus_record(item_id))
    for slug, source, target, keys, note in LOCALIZE_LABELS:
        _upsert(terms, _localize_system_record(f"system.{slug}", source, target, keys, note))
    _write(registry_path, registry)

    community_path = repo_root / "glossary/ui_community_terms.json"
    community = _load(community_path, {"terms": []})
    community_terms = community.setdefault("terms", [])

    for item_id in ("12", "13"):
        _upsert(community_terms, _login_bonus_community_record(item_id))
    for slug, source, target, keys, note in LOCALIZE_LABELS:
        _upsert(community_terms, _localize_community_record(f"common.{slug}", source, target, keys, note))
    _write(community_path, community)


if __name__ == "__main__":
    harden()

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


def _effect_record(record_id: str, alias: str, preferred: str, forbidden: list[str], basis: str) -> dict[str, Any]:
    return {
        "id": record_id,
        "source_aliases": [alias],
        "preferred": preferred,
        "accepted": [preferred],
        "compact": [],
        "forbidden": forbidden,
        "require_accepted": True,
        "source_paths": ["text_data_dict.json"],
        "json_path_prefixes": [["155"]],
        "match_mode": "contains",
        "invalidation_scope": "item",
        "basis": basis,
    }


def harden(repo_root: Path = REPO_ROOT) -> None:
    path = repo_root / "glossary/ui_community_terms.json"
    payload = _load(path, {"terms": []})
    terms = payload.setdefault("terms", [])

    records = [
        _effect_record(
            "support.friendship_bonus.effect155", "友情加成", "Friendship Bonus",
            ["Thưởng tình bạn", "thưởng tình bạn"],
            "Support Effect label in category 155; scope prevents ordinary friendship prose from matching.",
        ),
        _effect_record(
            "support.training_effectiveness.effect155", "训练效果提升", "Training Effectiveness",
            ["Tăng hiệu quả huấn luyện", "tăng hiệu quả huấn luyện", "Hiệu quả huấn luyện"],
            "Established Support Effect label for training effectiveness, limited to support-effect category 155.",
        ),
        {
            **_effect_record(
                "support.mood_effect.effect155", "干劲效果提升", "Mood Effect",
                ["Tăng hiệu ứng hứng khởi", "tăng hiệu ứng hứng khởi", "Hiệu ứng hứng khởi", "Thưởng Hứng khởi", "Thưởng hứng khởi"],
                "Established Support Effect label; narrower than the already-canonical generic Mood state.",
            ),
            "source_aliases": ["干劲效果提升", "心情加成"],
        },
        {
            **_effect_record(
                "support.initial_friendship.effect155", "初始牵绊值", "Initial Friendship",
                ["Liên kết ban đầu", "liên kết ban đầu", "Gắn kết ban đầu", "gắn kết ban đầu"],
                "Support Effect starting Friendship value; category scope avoids generic relationship prose.",
            ),
            "source_aliases": ["初始牵绊值", "初始羁绊值"],
        },
        _effect_record(
            "support.specialty_priority.effect155", "得意率提升", "Specialty Priority",
            ["Tăng tỷ lệ sở trường", "tăng tỷ lệ sở trường", "Tỷ lệ sở trường"],
            "Established Support Effect label for increased appearance at the card's specialty training.",
        ),
    ]

    bonus_terms = [
        ("speed", "速度加成", "Speed Bonus", ["Thưởng Tốc độ", "Thưởng tốc độ"]),
        ("stamina", "耐力加成", "Stamina Bonus", ["Thưởng Thể lực", "Thưởng thể lực"]),
        ("power", "力量加成", "Power Bonus", ["Thưởng Sức mạnh", "Thưởng sức mạnh"]),
        ("guts", "根性加成", "Guts Bonus", ["Thưởng Ý chí", "Thưởng ý chí"]),
        ("wit", "智力加成", "Wit Bonus", ["Thưởng Trí tuệ", "Thưởng trí tuệ"]),
        ("skill_pt", "技能Pt加成", "Skill Pt Bonus", ["Thưởng Điểm kỹ năng", "Thưởng điểm kỹ năng", "Thưởng Skill Pt"]),
    ]
    for slug, alias, preferred, forbidden in bonus_terms:
        records.append(
            _effect_record(
                f"support.{slug}_bonus.effect155", alias, preferred, forbidden,
                "Repeated player-facing Support Effect bonus label in category 155; ordinary stat prose remains unscoped.",
            )
        )

    for record in records:
        _upsert(terms, record)
    _write(path, payload)


if __name__ == "__main__":
    harden()

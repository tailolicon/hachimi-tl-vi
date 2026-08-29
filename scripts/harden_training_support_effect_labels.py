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


def harden(repo_root: Path = REPO_ROOT) -> None:
    path = repo_root / "glossary/ui_community_terms.json"
    payload = _load(path, {"terms": []})
    terms = payload.setdefault("terms", [])

    records = [
        {
            "id": "support.friendship_bonus.effect155",
            "source_aliases": ["友情加成"],
            "preferred": "Friendship Bonus",
            "accepted": ["Friendship Bonus"],
            "compact": [],
            "forbidden": ["Thưởng tình bạn", "thưởng tình bạn"],
            "require_accepted": True,
            "source_paths": ["text_data_dict.json"],
            "json_path_prefixes": [["155"]],
            "match_mode": "contains",
            "invalidation_scope": "item",
            "basis": "Support Effect label in category 155; scope prevents ordinary friendship prose from matching.",
        },
        {
            "id": "support.training_effectiveness.effect155",
            "source_aliases": ["训练效果提升"],
            "preferred": "Training Effectiveness",
            "accepted": ["Training Effectiveness"],
            "compact": [],
            "forbidden": ["Tăng hiệu quả huấn luyện", "tăng hiệu quả huấn luyện", "Hiệu quả huấn luyện"],
            "require_accepted": True,
            "source_paths": ["text_data_dict.json"],
            "json_path_prefixes": [["155"]],
            "match_mode": "contains",
            "invalidation_scope": "item",
            "basis": "Established Support Effect label for training effectiveness, limited to support-effect category 155.",
        },
        {
            "id": "support.mood_effect.effect155",
            "source_aliases": ["干劲效果提升"],
            "preferred": "Mood Effect",
            "accepted": ["Mood Effect"],
            "compact": [],
            "forbidden": ["Tăng hiệu ứng hứng khởi", "tăng hiệu ứng hứng khởi", "Hiệu ứng hứng khởi"],
            "require_accepted": True,
            "source_paths": ["text_data_dict.json"],
            "json_path_prefixes": [["155"]],
            "match_mode": "contains",
            "invalidation_scope": "item",
            "basis": "Established Support Effect label; this is narrower than the already-canonical generic Mood state.",
        },
        {
            "id": "support.initial_friendship.effect155",
            "source_aliases": ["初始牵绊值", "初始羁绊值"],
            "preferred": "Initial Friendship",
            "accepted": ["Initial Friendship"],
            "compact": [],
            "forbidden": ["Liên kết ban đầu", "liên kết ban đầu", "Gắn kết ban đầu", "gắn kết ban đầu"],
            "require_accepted": True,
            "source_paths": ["text_data_dict.json"],
            "json_path_prefixes": [["155"]],
            "match_mode": "contains",
            "invalidation_scope": "item",
            "basis": "Support Effect starting Friendship value; category scope avoids generic relationship prose.",
        },
        {
            "id": "support.specialty_priority.effect155",
            "source_aliases": ["得意率提升"],
            "preferred": "Specialty Priority",
            "accepted": ["Specialty Priority"],
            "compact": [],
            "forbidden": ["Tăng tỷ lệ sở trường", "tăng tỷ lệ sở trường", "Tỷ lệ sở trường"],
            "require_accepted": True,
            "source_paths": ["text_data_dict.json"],
            "json_path_prefixes": [["155"]],
            "match_mode": "contains",
            "invalidation_scope": "item",
            "basis": "Established Support Effect label for increased appearance at the card's specialty training.",
        },
    ]

    for record in records:
        _upsert(terms, record)
    _write(path, payload)


if __name__ == "__main__":
    harden()

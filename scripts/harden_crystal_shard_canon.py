from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]


def _upsert(terms: list[dict[str, Any]], record: dict[str, Any]) -> None:
    for item in terms:
        if item.get("id") == record["id"]:
            item.clear()
            item.update(record)
            return
    terms.append(record)


def harden(repo_root: Path = REPO_ROOT) -> None:
    path = repo_root / "glossary/source_bridge_terms.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    terms = payload.setdefault("terms", [])
    records = [
        {
            "id": "resource.crystal_shard",
            "ja": ["結晶片"],
            "zh_cn": ["结晶片", "結晶片"],
            "preferred": "Crystal Shards",
            "accepted": ["Crystal Shard", "Crystal Shards"],
            "forbidden": ["Mảnh kết tinh", "mảnh kết tinh"],
            "require_accepted": True,
            "source_paths": ["localize_dict.json"],
            "key_exact": ["Shop420161"],
            "match_mode": "contains",
            "note": "Shop420161 is the Crystal Shard Exchange heading; exact-key scope avoids literal crystal-fragment prose.",
        },
        {
            "id": "resource.crystal_shard.rainbow",
            "ja": ["虹の結晶片"],
            "zh_cn": ["彩虹结晶片", "彩虹結晶片"],
            "preferred": "Rainbow Crystal Shards",
            "accepted": ["Rainbow Crystal Shard", "Rainbow Crystal Shards"],
            "forbidden": ["Mảnh kết tinh Cầu vồng", "mảnh kết tinh cầu vồng"],
            "require_accepted": True,
            "source_paths": ["localize_dict.json"],
            "key_exact": ["Shop420162"],
            "match_mode": "contains",
            "note": "Shop420162 is the stable Rainbow Crystal Shard resource label.",
        },
        {
            "id": "resource.crystal_shard.gold",
            "ja": ["金の結晶片"],
            "zh_cn": ["金色结晶片", "金色結晶片"],
            "preferred": "Gold Crystal Shards",
            "accepted": ["Gold Crystal Shard", "Gold Crystal Shards"],
            "forbidden": ["Mảnh kết tinh Vàng", "mảnh kết tinh vàng"],
            "require_accepted": True,
            "source_paths": ["localize_dict.json"],
            "key_exact": ["Shop420163"],
            "match_mode": "contains",
            "note": "Shop420163 is the stable Gold Crystal Shard resource label.",
        },
    ]
    for record in records:
        _upsert(terms, record)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    harden()

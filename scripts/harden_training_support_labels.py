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
    registry_path = repo_root / "glossary/term_registry.json"
    registry = _load(registry_path, {"terms": []})
    terms = registry.setdefault("terms", [])

    _upsert(
        terms,
        {
            "id": "training.level.outgame352008",
            "category": "training",
            "ja": ["トレーニングLv", "トレーニングレベル"],
            "zh_cn": ["训练等级"],
            "target_vi": "Training Level",
            "locked": True,
            "source_paths": ["localize_dict.json"],
            "json_path_prefixes": [["Outgame352008"]],
            "match_mode": "exact",
            "invalidation_scope": "item",
            "note": (
                "Outgame352008 is the player-facing training-facility level label. Keep the established English "
                "system term Training Level; do not globally match ordinary prose about training or levels."
            ),
        },
    )
    _upsert(
        terms,
        {
            "id": "training.failure_rate.singlemode0036",
            "category": "training",
            "ja": ["失敗率"],
            "zh_cn": ["失败率"],
            "target_vi": "Failure Rate",
            "locked": True,
            "source_paths": ["localize_dict.json"],
            "json_path_prefixes": [["SingleMode0036"]],
            "match_mode": "exact",
            "invalidation_scope": "item",
            "note": (
                "SingleMode0036 is the Career training probability label shown before training. Use Failure Rate; "
                "the exact localize path prevents generic narrative failure wording from matching."
            ),
        },
    )
    _write(registry_path, registry)

    community_path = repo_root / "glossary/ui_community_terms.json"
    community = _load(community_path, {"terms": []})
    community_terms = community.setdefault("terms", [])

    _upsert(
        community_terms,
        {
            "id": "common.training_level.outgame352008",
            "source_aliases": ["训练等级"],
            "preferred": "Training Level",
            "accepted": ["Training Level"],
            "compact": ["Training Lv"],
            "forbidden": ["Cấp huấn luyện", "cấp huấn luyện"],
            "require_accepted": True,
            "source_paths": ["localize_dict.json"],
            "key_exact": ["Outgame352008"],
            "match_mode": "exact",
            "invalidation_scope": "item",
            "basis": (
                "Established English player terminology for the per-facility training level. Exact-key scope avoids "
                "turning generic level/training prose into a fixed system label."
            ),
        },
    )
    _upsert(
        community_terms,
        {
            "id": "common.failure_rate.singlemode0036",
            "source_aliases": ["失败率"],
            "preferred": "Failure Rate",
            "accepted": ["Failure Rate"],
            "compact": [],
            "forbidden": ["Tỷ lệ thất bại", "tỷ lệ thất bại"],
            "require_accepted": True,
            "source_paths": ["localize_dict.json"],
            "key_exact": ["SingleMode0036"],
            "match_mode": "exact",
            "invalidation_scope": "item",
            "basis": (
                "Established English Career-training UI term for the displayed probability of training failure. "
                "Exact-key scope avoids matching ordinary narrative failure wording."
            ),
        },
    )
    _write(community_path, community)


if __name__ == "__main__":
    harden()

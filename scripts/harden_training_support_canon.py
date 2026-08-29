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

    # Friendship Training is an established player-facing system term. The
    # historical Vietnamese calque was already surfacing as a locked mismatch
    # in the retrospective corpus. Keep the full compound only: bare
    # friendship/training words remain ordinary prose.
    _upsert(
        terms,
        {
            "id": "system.friendship_training",
            "category": "training",
            "ja": ["友情トレーニング"],
            "zh_cn": ["友情训练"],
            "target_vi": "Friendship Training",
            "locked": True,
            "match_mode": "contains",
            "invalidation_scope": "item",
            "note": (
                "Player-facing training mechanic. Use Friendship Training; do not calque as "
                "Huấn luyện Hữu nghị/huấn luyện tình bạn. The rule matches only the full mechanic compound."
            ),
        },
    )
    _write(registry_path, registry)

    community_path = repo_root / "glossary/ui_community_terms.json"
    community = _load(community_path, {"terms": []})
    _upsert(
        community.setdefault("terms", []),
        {
            "id": "common.friendship_training",
            "source_aliases": ["友情トレーニング", "友情训练"],
            "preferred": "Friendship Training",
            "accepted": ["Friendship Training"],
            "compact": [],
            "forbidden": ["Huấn luyện Hữu nghị", "huấn luyện hữu nghị", "Huấn luyện tình bạn", "huấn luyện tình bạn"],
            "require_accepted": True,
            "match_mode": "contains",
            "invalidation_scope": "item",
            "basis": (
                "Established player-facing term for the rainbow training mechanic. Full-compound aliases only; "
                "generic friendship/training prose is intentionally not matched."
            ),
        },
    )
    _write(community_path, community)


if __name__ == "__main__":
    harden()

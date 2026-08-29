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


def _find(items: list[dict[str, Any]], record_id: str) -> dict[str, Any] | None:
    for item in items:
        if isinstance(item, dict) and str(item.get("id", "")) == record_id:
            return item
    return None


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

    # The historical progress.bond record globally locked bare 絆/羁绊 to the
    # Vietnamese calque Gắn kết. Bare friendship/bond language is ambiguous in
    # prose, while the support-effect table has a concrete gauge mechanic. Keep
    # the umbrella ID as documentation only and enforce the gauge narrowly.
    bond_umbrella = _find(terms, "progress.bond")
    if bond_umbrella is not None:
        bond_umbrella["ja"] = []
        bond_umbrella["zh_cn"] = []
        bond_umbrella["locked"] = False
        bond_umbrella["note"] = (
            "Umbrella friendship/bond vocabulary only. Bare 絆/羁绊 is intentionally not globally locked; "
            "use scoped Friendship Gauge records for proven gameplay gauge contexts."
        )

    _upsert(
        terms,
        {
            "id": "progress.friendship_gauge.support_effects",
            "category": "progression",
            "ja": ["絆ゲージ"],
            "zh_cn": ["羁绊值"],
            "target_vi": "Friendship Gauge",
            "locked": True,
            "source_paths": ["text_data_dict.json"],
            "json_path_prefixes": [["155"]],
            "match_mode": "contains",
            "invalidation_scope": "item",
            "note": (
                "Support-effect descriptions in text_data category 155 use 羁绊值 for the Support Card Friendship Gauge. "
                "Do not generalize bare friendship/bond prose to this system label."
            ),
        },
    )

    _upsert(
        terms,
        {
            "id": "resource.support_points.common0160",
            "category": "resource",
            "ja": ["サポートPt", "サポートポイント"],
            "zh_cn": ["支援点数"],
            "target_vi": "Support Pt",
            "locked": True,
            "source_paths": ["localize_dict.json"],
            "key_exact": ["Common0160"],
            "match_mode": "exact",
            "invalidation_scope": "item",
            "note": (
                "Common0160 is the compact Support Points resource label. Use Support Pt in the UI; "
                "Support Points remains acceptable in prose."
            ),
        },
    )

    _upsert(
        terms,
        {
            "id": "state.energy.singlemode",
            "category": "training",
            "ja": ["体力"],
            "zh_cn": ["体力"],
            "target_vi": "Energy",
            "locked": True,
            "source_paths": ["localize_dict.json"],
            "key_exact": ["SingleMode0006", "SingleMode0074", "SingleMode0075"],
            "match_mode": "contains",
            "invalidation_scope": "item",
            "note": (
                "These SingleMode slots are the Career training Energy gauge and its gain/loss messages. "
                "Scope is exact so ordinary prose about physical strength is not forced to Energy."
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
    _upsert(
        community_terms,
        {
            "id": "common.friendship_gauge.support_effects",
            "source_aliases": ["羁绊值"],
            "preferred": "Friendship Gauge",
            "accepted": ["Friendship Gauge"],
            "compact": [],
            "forbidden": ["Gắn kết", "gắn kết", "Giá trị liên kết", "giá trị liên kết"],
            "require_accepted": True,
            "source_paths": ["text_data_dict.json"],
            "json_path_prefixes": [["155"]],
            "match_mode": "contains",
            "invalidation_scope": "item",
            "basis": (
                "Category 155 support-effect descriptions refer to the Support Card Friendship Gauge. "
                "Bare 羁绊 remains ordinary friendship/bond language outside this scoped mechanic."
            ),
        },
    )
    _upsert(
        community_terms,
        {
            "id": "common.support_points.common0160",
            "source_aliases": ["支援点数"],
            "preferred": "Support Pt",
            "accepted": ["Support Pt", "Support Pts", "Support Points"],
            "compact": [],
            "forbidden": ["Điểm Hỗ trợ", "Điểm hỗ trợ", "điểm hỗ trợ"],
            "require_accepted": True,
            "source_paths": ["localize_dict.json"],
            "key_exact": ["Common0160"],
            "match_mode": "exact",
            "invalidation_scope": "item",
            "basis": (
                "Common0160 is the player-facing Support Points resource label. Compact UI uses Support Pt; "
                "plural prose may use Support Pts or Support Points."
            ),
        },
    )
    _upsert(
        community_terms,
        {
            "id": "common.energy.singlemode",
            "source_aliases": ["体力"],
            "preferred": "Energy",
            "accepted": ["Energy"],
            "compact": [],
            "forbidden": ["Thể lực", "thể lực"],
            "require_accepted": True,
            "source_paths": ["localize_dict.json"],
            "key_exact": ["SingleMode0006", "SingleMode0074", "SingleMode0075"],
            "match_mode": "contains",
            "invalidation_scope": "item",
            "basis": (
                "Exact Career training UI slots for the Energy gauge and its gain/loss messages. "
                "The key guard prevents ordinary physical-strength prose from matching."
            ),
        },
    )
    _write(community_path, community)


if __name__ == "__main__":
    harden()

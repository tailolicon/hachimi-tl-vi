from __future__ import annotations

"""Canonicalize the in-game ウマ娘ステークス race-name component in text data."""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FINDING_ID = "cf-0dae34861911a969"
SOURCE_ZH = "赛马娘锦标"
SOURCE_JA = "ウマ娘ステークス"
PREFERRED = "Uma Musume Stakes"
TERM_ID = "race.uma_musume_stakes.component131"
WORLD_TERM_ID = "common.world.umamusume"

TERM = {
    "id": TERM_ID,
    "category": "race",
    "source_aliases": [SOURCE_ZH],
    "preferred": PREFERRED,
    "compact": [],
    "accepted": [PREFERRED],
    "forbidden": ["Mã Nương Stakes", "Mã Nương Cúp", SOURCE_ZH],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [],
    "match_mode": "contains",
    "basis": (
        "The generated finding is source-path scoped rather than category scoped. "
        "赛马娘锦标 is the game-specific race-name component JP ウマ娘ステークス wherever it occurs in text_data_dict.json. "
        "Existing locked race names such as 府中ウマ娘ステークス -> Fuchu Uma Musume Stakes and "
        "福島ウマ娘ステークス -> Fukushima Uma Musume Stakes establish the project convention: preserve "
        "Uma Musume and Stakes rather than applying generic Mã Nương."
    ),
}

DECISION = {
    "decision_id": "audit.finding.uma-musume-stakes-component",
    "source_zh_cn": SOURCE_ZH,
    "action": "lock",
    "target_vi": PREFERRED,
    "kind": "race_name",
    "category": "race",
    "ja": [SOURCE_JA],
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [],
    "match_mode": "contains",
    "note": (
        "Lock the race-name component 赛马娘锦标 to Uma Musume Stakes throughout text_data_dict.json. "
        "The live finding itself has no JSON-path prefix, so a category-131-only rule cannot cover it. "
        "This follows the verified 府中/福島ウマ娘ステークス naming convention and prevents generic "
        "赛马娘 -> Mã Nương from firing inside race proper names."
    ),
}


def _load(path: Path, default: dict[str, Any] | None = None) -> dict[str, Any]:
    if not path.exists():
        return dict(default or {})
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def _upsert(items: list[Any], record: dict[str, Any], *, id_field: str) -> None:
    record_id = str(record[id_field])
    for index, item in enumerate(items):
        if isinstance(item, dict) and str(item.get(id_field) or "") == record_id:
            merged = dict(item)
            merged.update(record)
            items[index] = merged
            return
    items.append(dict(record))


def harden(repo_root: Path = ROOT) -> bool:
    changed = False

    community_path = repo_root / "glossary" / "ui_community_terms.json"
    community = _load(community_path, {"schema_version": 1, "terms": []})
    terms = community.setdefault("terms", [])
    if not isinstance(terms, list):
        raise ValueError("glossary/ui_community_terms.json terms must be a list")
    before = json.dumps(community, ensure_ascii=False, sort_keys=True)

    world = next(
        (item for item in terms if isinstance(item, dict) and item.get("id") == WORLD_TERM_ID),
        None,
    )
    if world is None:
        raise ValueError(f"missing canonical community term {WORLD_TERM_ID}")
    exclusions = [str(value) for value in world.get("exclude_source_contains", []) if str(value)]
    world["exclude_source_contains"] = list(dict.fromkeys([*exclusions, SOURCE_ZH]))
    world["basis"] = (
        "Generic 赛马娘 is the project world/species term Mã Nương, but it must not fire inside established "
        "ウマ娘ステークス race-name forms represented by 赛马娘锦标."
    )

    _upsert(terms, TERM, id_field="id")
    if before != json.dumps(community, ensure_ascii=False, sort_keys=True):
        _write(community_path, community)
        changed = True

    reviews_path = repo_root / "glossary" / "terminology_reviews.json"
    reviews = _load(reviews_path, {"schema_version": 1, "decisions": []})
    decisions = reviews.setdefault("decisions", [])
    if not isinstance(decisions, list):
        raise ValueError("glossary/terminology_reviews.json decisions must be a list")
    before = json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    _upsert(decisions, DECISION, id_field="decision_id")
    if before != json.dumps(reviews, ensure_ascii=False, sort_keys=True):
        _write(reviews_path, reviews)
        changed = True

    return changed


def main() -> int:
    changed = harden(ROOT)
    print(f"uma_musume_stakes_component_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

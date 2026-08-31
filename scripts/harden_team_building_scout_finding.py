from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TEAM_BUILDING_KEYS = [
    "TeamBuilding020022",
    "TeamBuilding020023",
    "TeamBuilding020025",
    "TeamBuilding030008",
]

TEAM_BUILDING_SCOUT = {
    "id": "event.aim_for_the_stars.scout",
    "category": "event",
    "source_aliases": ["签约"],
    "preferred": "Scout",
    "compact": [],
    "accepted": ["Scout", "Scouting"],
    "forbidden": ["Ký hợp đồng", "ký hợp đồng", "Hợp đồng", "hợp đồng"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["localize_dict.json"],
    "key_exact": TEAM_BUILDING_KEYS,
    "match_mode": "contains",
    "basis": "In the Aim for the Stars!/Team Building event, this action is the player-facing scouting mechanic, not literal contract signing. GameTora's event guide consistently describes spending Scout Points to scout characters. The rule is restricted to the four proven TeamBuilding UI keys so ordinary contract language remains unaffected.",
}

TEAM_BUILDING_SCOUT_POINTS = {
    "id": "event.aim_for_the_stars.scout_points",
    "category": "event_resource",
    "source_aliases": ["签约Pt"],
    "preferred": "Scout Points",
    "compact": ["Scout Pt"],
    "accepted": ["Scout Points", "Scout Pt"],
    "forbidden": ["Điểm ký hợp đồng", "Điểm Scout", "Contract Points"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["localize_dict.json"],
    "key_exact": ["TeamBuilding020023", "TeamBuilding020025"],
    "match_mode": "contains",
    "basis": "Aim for the Stars! uses Scout Points as the event currency for scouting characters. Scope is limited to the proven TeamBuilding UI keys containing 签约Pt.",
}

TEAM_BUILDING_SCOUT_DECISION = {
    "decision_id": "audit.finding.aim-for-the-stars-scout",
    "source_zh_cn": "签约",
    "action": "lock",
    "target_vi": "Scout",
    "kind": "terminology",
    "category": "event",
    "note": "Aim for the Stars!/Team Building scouting action. Do not translate this scoped event use as literal contract signing; event-specific matching is enforced by event.aim_for_the_stars.scout.",
}

TEAM_BUILDING_SCOUT_POINTS_DECISION = {
    "decision_id": "audit.finding.aim-for-the-stars-scout-points",
    "source_zh_cn": "签约Pt",
    "action": "lock",
    "target_vi": "Scout Points",
    "kind": "terminology",
    "category": "event_resource",
    "note": "Player-facing Aim for the Stars! event currency used to scout characters; scoped community rule prevents unrelated 签约 uses from matching.",
}


def _load(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return dict(default)
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _upsert(items: list[Any], record: dict[str, Any], *, id_field: str) -> None:
    record_id = str(record[id_field])
    for index, item in enumerate(items):
        if isinstance(item, dict) and str(item.get(id_field) or "") == record_id:
            merged = dict(item)
            merged.update(record)
            items[index] = merged
            return
    items.append(record)


def harden(repo_root: Path = ROOT) -> bool:
    changed = False

    community_path = repo_root / "glossary" / "ui_community_terms.json"
    community = _load(community_path, {"schema_version": 1, "terms": []})
    before = json.dumps(community, ensure_ascii=False, sort_keys=True)
    terms = community.setdefault("terms", [])
    _upsert(terms, TEAM_BUILDING_SCOUT, id_field="id")
    _upsert(terms, TEAM_BUILDING_SCOUT_POINTS, id_field="id")
    if json.dumps(community, ensure_ascii=False, sort_keys=True) != before:
        _write(community_path, community)
        changed = True

    reviews_path = repo_root / "glossary" / "terminology_reviews.json"
    reviews = _load(reviews_path, {"schema_version": 1, "decisions": []})
    before = json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    decisions = reviews.setdefault("decisions", [])
    _upsert(decisions, TEAM_BUILDING_SCOUT_DECISION, id_field="decision_id")
    _upsert(decisions, TEAM_BUILDING_SCOUT_POINTS_DECISION, id_field="decision_id")
    if json.dumps(reviews, ensure_ascii=False, sort_keys=True) != before:
        _write(reviews_path, reviews)
        changed = True

    return changed


def main() -> int:
    changed = harden(ROOT)
    print("updated" if changed else "already-current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

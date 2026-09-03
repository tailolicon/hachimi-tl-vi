from __future__ import annotations

"""Canonicalize Legend Race / Daily Legend Race in transfer-warning items."""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

LEGEND_SOURCE = "传奇比赛"
LEGEND_TARGET = "Legend Race"
LEGEND_KEY = "Character0335"
LEGEND_FINDING_ID = "cf-cf51d5270ed06b18"

DAILY_SOURCE = "每日传奇比赛"
DAILY_TARGET = "Daily Legend Race"
DAILY_KEY = "Character408001"
DAILY_FINDING_ID = "cf-6f1b22f01d3e293a"

TERMS = [
    {
        "id": "event.legend_race.transfer_notice",
        "category": "event",
        "source_aliases": [LEGEND_SOURCE],
        "preferred": LEGEND_TARGET,
        "compact": [],
        "accepted": [LEGEND_TARGET],
        "forbidden": ["Giải đấu Huyền thoại"],
        "require_accepted": True,
        "invalidation_scope": "item",
        "source_paths": ["localize_dict.json"],
        "key_exact": [LEGEND_KEY],
        "match_mode": "contains",
        "basis": (
            "Stable Global key Character0335 names the game mode Legend Race inside the transfer notice. "
            "Use the released proper name and keep the matcher item-scoped."
        ),
    },
    {
        "id": "event.daily_legend_race.transfer_notice",
        "category": "event",
        "source_aliases": [DAILY_SOURCE],
        "preferred": DAILY_TARGET,
        "compact": [],
        "accepted": [DAILY_TARGET],
        "forbidden": ["Đua Huyền thoại Hằng ngày"],
        "require_accepted": True,
        "invalidation_scope": "item",
        "source_paths": ["localize_dict.json"],
        "key_exact": [DAILY_KEY],
        "match_mode": "contains",
        "basis": (
            "Stable Global key Character408001 names the game mode Daily Legend Race inside the transfer notice. "
            "Use the released proper name and keep the matcher item-scoped."
        ),
    },
]

DECISIONS = [
    {
        "decision_id": "audit.finding.legend-race-transfer-notice",
        "source_zh_cn": LEGEND_SOURCE,
        "action": "lock",
        "target_vi": LEGEND_TARGET,
        "kind": "proper_name",
        "category": "event",
        "en": [LEGEND_TARGET],
        "note": (
            "Finding is scoped to Character0335; maintained Global-English data uses Legend Race in the same notice."
        ),
    },
    {
        "decision_id": "audit.finding.daily-legend-race-transfer-notice",
        "source_zh_cn": DAILY_SOURCE,
        "action": "lock",
        "target_vi": DAILY_TARGET,
        "kind": "proper_name",
        "category": "event",
        "en": [DAILY_TARGET],
        "note": (
            "Finding is scoped to Character408001; maintained Global-English data uses Daily Legend Race in the same notice."
        ),
    },
]


def _load(path: Path, default: dict[str, Any] | None = None) -> dict[str, Any]:
    if not path.exists():
        return dict(default or {})
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
    items.append(dict(record))


def harden(repo_root: Path = ROOT) -> bool:
    changed = False

    community_path = repo_root / "glossary" / "ui_community_terms.json"
    community = _load(community_path, {"schema_version": 1, "terms": []})
    terms = community.setdefault("terms", [])
    if not isinstance(terms, list):
        raise ValueError("glossary/ui_community_terms.json terms must be a list")
    before = json.dumps(community, ensure_ascii=False, sort_keys=True)
    for term in TERMS:
        _upsert(terms, term, id_field="id")
    if before != json.dumps(community, ensure_ascii=False, sort_keys=True):
        _write(community_path, community)
        changed = True

    reviews_path = repo_root / "glossary" / "terminology_reviews.json"
    reviews = _load(reviews_path, {"schema_version": 1, "decisions": []})
    decisions = reviews.setdefault("decisions", [])
    if not isinstance(decisions, list):
        raise ValueError("glossary/terminology_reviews.json decisions must be a list")
    before = json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    for decision in DECISIONS:
        _upsert(decisions, decision, id_field="decision_id")
    if before != json.dumps(reviews, ensure_ascii=False, sort_keys=True):
        _write(reviews_path, reviews)
        changed = True

    return changed


def main() -> int:
    changed = harden(ROOT)
    print(f"legend_races_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

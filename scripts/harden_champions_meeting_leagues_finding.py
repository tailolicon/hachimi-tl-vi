from __future__ import annotations

"""Canonicalize the two Champions Meeting league-class UI labels."""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

OPEN_SOURCE = "公开联赛"
OPEN_TARGET = "Open League"
OPEN_FINDING_ID = "cf-10ef1d1f7bea118d"

GRADED_SOURCE = "等级联赛"
GRADED_TARGET = "Graded League"
GRADED_FINDING_ID = "cf-c0936acad5f22c2f"

TERMS = [
    {
        "id": "event.champions_meeting.open_league",
        "category": "event",
        "source_aliases": [OPEN_SOURCE],
        "preferred": OPEN_TARGET,
        "compact": [],
        "accepted": [OPEN_TARGET],
        "forbidden": ["Giải đấu mở"],
        "require_accepted": True,
        "invalidation_scope": "item",
        "source_paths": ["localize_dict.json"],
        "match_mode": "exact",
        "basis": (
            "Stable Global key Champions0601 is released as Open League. Keep the "
            "established Champions Meeting league label instead of a literal Vietnamese paraphrase."
        ),
    },
    {
        "id": "event.champions_meeting.graded_league",
        "category": "event",
        "source_aliases": [GRADED_SOURCE],
        "preferred": GRADED_TARGET,
        "compact": [],
        "accepted": [GRADED_TARGET],
        "forbidden": ["Giải đấu theo hạng"],
        "require_accepted": True,
        "invalidation_scope": "item",
        "source_paths": ["localize_dict.json"],
        "match_mode": "exact",
        "basis": (
            "Stable Global key Champions0602 is released as Graded League. Keep the "
            "established Champions Meeting league label instead of a literal Vietnamese paraphrase."
        ),
    },
]

DECISIONS = [
    {
        "decision_id": "audit.finding.champions-meeting-open-league",
        "source_zh_cn": OPEN_SOURCE,
        "action": "lock",
        "target_vi": OPEN_TARGET,
        "kind": "system_label",
        "category": "event",
        "en": [OPEN_TARGET],
        "note": (
            "Stable key Champions0601 is Open League in maintained Global-English Hachimi data, "
            "and current Global Champions Meeting terminology uses the same released label."
        ),
    },
    {
        "decision_id": "audit.finding.champions-meeting-graded-league",
        "source_zh_cn": GRADED_SOURCE,
        "action": "lock",
        "target_vi": GRADED_TARGET,
        "kind": "system_label",
        "category": "event",
        "en": [GRADED_TARGET],
        "note": (
            "Stable key Champions0602 is Graded League in maintained Global-English Hachimi data, "
            "and current Global Champions Meeting terminology uses the same released label."
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
    print(f"champions_meeting_leagues_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

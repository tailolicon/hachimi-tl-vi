from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

AIM_FOR_THE_STARS = {
    "id": "event.aim_for_the_stars",
    "category": "event",
    "source_aliases": ["目标是！最强队伍"],
    "preferred": "Aim for the Stars!",
    "compact": [],
    "accepted": ["Aim for the Stars!"],
    "forbidden": ["Hướng tới! Đội mạnh nhất", "Mục tiêu là! Đội mạnh nhất"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [["10"]],
    "match_mode": "contains",
    "basis": "Named JP event 目指せ！最強チーム. Current established English community reference GameTora uses Aim for the Stars!; scope is restricted to item/ticket text in text_data category 10.",
}

AIM_FOR_THE_STARS_DECISION = {
    "decision_id": "audit.finding.aim-for-the-stars",
    "source_zh_cn": "目标是！最强队伍",
    "action": "lock",
    "target_vi": "Aim for the Stars!",
    "kind": "proper_name",
    "category": "event",
    "note": "Verified JP identity 目指せ！最強チーム; use the established English community event title Aim for the Stars! until an official Global title supersedes it. Canonical matching stays scoped to text_data category 10.",
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
    _upsert(terms, AIM_FOR_THE_STARS, id_field="id")
    if before != json.dumps(community, ensure_ascii=False, sort_keys=True):
        _write(community_path, community)
        changed = True

    reviews_path = repo_root / "glossary" / "terminology_reviews.json"
    reviews = _load(reviews_path, {"schema_version": 1, "decisions": []})
    decisions = reviews.setdefault("decisions", [])
    if not isinstance(decisions, list):
        raise ValueError("glossary/terminology_reviews.json decisions must be a list")
    before = json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    _upsert(decisions, AIM_FOR_THE_STARS_DECISION, id_field="decision_id")
    if before != json.dumps(reviews, ensure_ascii=False, sort_keys=True):
        _write(reviews_path, reviews)
        changed = True
    return changed


def main() -> int:
    changed = harden(ROOT)
    print(f"strongest_team_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

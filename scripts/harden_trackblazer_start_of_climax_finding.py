from __future__ import annotations

"""Resolve the Trackblazer / Make a new track!! scenario subtitle canonical finding."""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FINDING_ID = "cf-a95679214256d891"
SOURCE_ZH = "巅峰赛开幕"
SOURCE_JA = "クライマックス開幕"
TARGET = "Start of the Climax"
RULE_ID = "scenario.trackblazer.start_of_the_climax"
DECISION_ID = "audit.finding.trackblazer-start-of-the-climax"

RULE = {
    "id": RULE_ID,
    "category": "system_label",
    "source_aliases": [SOURCE_ZH],
    "preferred": TARGET,
    "compact": [],
    "accepted": [TARGET],
    "forbidden": ["Climax khai mạc", "Khai mạc Climax"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [],
    "match_mode": "contains",
    "basis": (
        "The zh-CN subtitle 巅峰赛开幕 is the localized bridge for JP クライマックス開幕 in the "
        "third Career scenario. The released Global scenario is Trackblazer: Start of the Climax, "
        "so preserve the player-facing Global subtitle Start of the Climax rather than the mixed "
        "Vietnamese calque Climax khai mạc."
    ),
}

DECISION = {
    "decision_id": DECISION_ID,
    "source_zh_cn": SOURCE_ZH,
    "action": "lock",
    "target_vi": TARGET,
    "kind": "system_label",
    "category": "system_label",
    "ja": [SOURCE_JA],
    "note": (
        "Global released Trackblazer under the title Trackblazer: Start of the Climax. "
        "This resolves the source-bridge subtitle without inventing a Vietnamese scenario title."
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
    _upsert(terms, RULE, id_field="id")
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
    print(f"trackblazer_start_of_climax_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

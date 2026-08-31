from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

MECHA_EN = {
    "id": "scenario.mecha.en.text131",
    "category": "system_label",
    "source_aliases": ["机械EN"],
    "preferred": "Mecha EN",
    "compact": [],
    "accepted": ["Mecha EN"],
    "forbidden": ["Cơ khí EN", "EN cơ khí"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [["131"]],
    "match_mode": "contains",
    "basis": "Run! Mecha Umamusume scenario resource allocated to ST-2 core chips. Established English scenario guides call it Mecha EN. Scope category 131 mission/system text to avoid broad EN substring matching.",
}

MECHA_EN_DECISION = {
    "decision_id": "audit.finding.mecha-en",
    "source_zh_cn": "机械EN",
    "action": "lock",
    "target_vi": "Mecha EN",
    "kind": "system_label",
    "category": "system_label",
    "note": "Named Run! Mecha Umamusume tuning resource; preserve player-facing Mecha EN.",
}


def _load(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return dict(default)
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def _upsert(items: list[Any], record: dict[str, Any], field: str) -> None:
    rid = str(record[field])
    for index, item in enumerate(items):
        if isinstance(item, dict) and str(item.get(field) or "") == rid:
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
        raise ValueError("community terms must be a list")
    before = json.dumps(community, ensure_ascii=False, sort_keys=True)
    _upsert(terms, MECHA_EN, "id")
    if before != json.dumps(community, ensure_ascii=False, sort_keys=True):
        _write(community_path, community)
        changed = True

    reviews_path = repo_root / "glossary" / "terminology_reviews.json"
    reviews = _load(reviews_path, {"schema_version": 1, "decisions": []})
    decisions = reviews.setdefault("decisions", [])
    if not isinstance(decisions, list):
        raise ValueError("review decisions must be a list")
    before = json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    _upsert(decisions, MECHA_EN_DECISION, "decision_id")
    if before != json.dumps(reviews, ensure_ascii=False, sort_keys=True):
        _write(reviews_path, reviews)
        changed = True
    return changed


def main() -> int:
    print(f"mecha_en_hardening_changed={str(harden(ROOT)).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

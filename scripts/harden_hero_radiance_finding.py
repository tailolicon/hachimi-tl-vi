from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

HERO_RADIANCE = {
    "id": "condition.zenno_rob_roy.heros_radiance",
    "category": "condition",
    "source_aliases": ["英雄的光辉"],
    "preferred": "Hero's Radiance",
    "compact": [],
    "accepted": ["Hero's Radiance"],
    "forbidden": ["Ánh hào quang anh hùng"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [["142"]],
    "match_mode": "exact",
    "basis": "Verified Zenno Rob Roy Career Condition identity: zh-CN 英雄的光辉 maps to JP 英雄の光輝, the special Condition used for her final Arima Kinen. No official Global Condition label is established in the current evidence, so use a direct player-facing English rendering and keep the rule confined to the Condition-name table.",
}

HERO_RADIANCE_DECISION = {
    "decision_id": "audit.finding.condition-zenno-rob-roy-heros-radiance",
    "source_zh_cn": "英雄的光辉",
    "action": "lock",
    "target_vi": "Hero's Radiance",
    "kind": "condition",
    "category": "condition",
    "note": "Verified against JP 英雄の光輝, Zenno Rob Roy's Career Condition for the final Arima Kinen; direct English rendering is used pending an official Global label.",
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


def _upsert(items: list[Any], record: dict[str, Any], id_field: str) -> None:
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
    before = json.dumps(community, ensure_ascii=False, sort_keys=True)
    _upsert(community.setdefault("terms", []), HERO_RADIANCE, "id")
    if before != json.dumps(community, ensure_ascii=False, sort_keys=True):
        _write(community_path, community)
        changed = True

    reviews_path = repo_root / "glossary" / "terminology_reviews.json"
    reviews = _load(reviews_path, {"schema_version": 1, "decisions": []})
    before = json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    _upsert(reviews.setdefault("decisions", []), HERO_RADIANCE_DECISION, "decision_id")
    if before != json.dumps(reviews, ensure_ascii=False, sort_keys=True):
        _write(reviews_path, reviews)
        changed = True

    return changed


def main() -> int:
    changed = harden(ROOT)
    print(f"hero_radiance_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

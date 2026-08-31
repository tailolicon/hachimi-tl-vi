from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

MECHA_TERMS = (
    {
        "id": "scenario.mecha.gear.text131",
        "source": "机械齿轮",
        "target": "Mecha Gear",
        "forbidden": ["Bánh răng Mecha", "bánh răng Mecha"],
        "basis": "Run! Mecha Umamusume training icon/mechanic. English scenario guides call the per-training icon a Mecha Gear and describe Gears appearing during training.",
        "slug": "mecha-gear",
    },
    {
        "id": "scenario.mecha.research_level.text131",
        "source": "研究Lv",
        "target": "Research Level",
        "forbidden": ["Lv Nghiên cứu", "Cấp Nghiên cứu", "cấp nghiên cứu"],
        "basis": "Run! Mecha Umamusume progression metric. GameTora consistently calls it Research level; use the player-facing English system label in missions and mechanics text.",
        "slug": "research-level",
    },
    {
        "id": "scenario.mecha.overdrive.text131",
        "source": "超速驱动",
        "target": "Overdrive",
        "forbidden": ["Siêu tốc", "Tăng tốc vượt mức"],
        "basis": "Run! Mecha Umamusume scenario mechanic with an Overdrive Gauge. Established English guides call the stored/activated mechanic Overdrive.",
        "slug": "overdrive",
    },
)


def _term(spec: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": spec["id"],
        "category": "system_label",
        "source_aliases": [spec["source"]],
        "preferred": spec["target"],
        "compact": [],
        "accepted": [spec["target"]],
        "forbidden": spec["forbidden"],
        "require_accepted": True,
        "invalidation_scope": "item",
        "source_paths": ["text_data_dict.json"],
        "json_path_prefixes": [["131"]],
        "match_mode": "contains",
        "basis": spec["basis"],
    }


def _decision(spec: dict[str, Any]) -> dict[str, Any]:
    return {
        "decision_id": f"audit.finding.{spec['slug']}",
        "source_zh_cn": spec["source"],
        "action": "lock",
        "target_vi": spec["target"],
        "kind": "system_label",
        "category": "system_label",
        "note": f"Named Run! Mecha Umamusume system label; preserve {spec['target']} in category-131 mission/mechanics text.",
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
    for spec in MECHA_TERMS:
        _upsert(terms, _term(spec), "id")
    if before != json.dumps(community, ensure_ascii=False, sort_keys=True):
        _write(community_path, community)
        changed = True

    reviews_path = repo_root / "glossary" / "terminology_reviews.json"
    reviews = _load(reviews_path, {"schema_version": 1, "decisions": []})
    decisions = reviews.setdefault("decisions", [])
    if not isinstance(decisions, list):
        raise ValueError("review decisions must be a list")
    before = json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    for spec in MECHA_TERMS:
        _upsert(decisions, _decision(spec), "decision_id")
    if before != json.dumps(reviews, ensure_ascii=False, sort_keys=True):
        _write(reviews_path, reviews)
        changed = True
    return changed


def main() -> int:
    print(f"mecha_system_hardening_changed={str(harden(ROOT)).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

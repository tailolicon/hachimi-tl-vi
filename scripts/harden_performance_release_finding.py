from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

PERFORMANCE_RELEASE = {
    "id": "support.performance_release.localize",
    "category": "system_label",
    "source_aliases": ["性能解放"],
    "preferred": "Performance Release",
    "compact": [],
    "accepted": ["Performance Release"],
    "forbidden": ["mở khóa tiềm năng", "Mở khóa tiềm năng", "giải phóng hiệu năng", "Giải phóng hiệu năng"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["localize_dict.json"],
    "match_mode": "contains",
    "basis": "Support-card progression system introduced with the 4.5th-anniversary support-card overhaul: JP 上限解放 was replaced by 性能解放, with support effects applied by release stage. Use Performance Release to distinguish this support-card mechanic from trainee Potential.",
}

PERFORMANCE_RELEASE_DECISION = {
    "decision_id": "audit.finding.performance-release",
    "source_zh_cn": "性能解放",
    "action": "lock",
    "target_vi": "Performance Release",
    "kind": "system_label",
    "category": "system_label",
    "note": "Named support-card progression mechanic after the 4.5th-anniversary overhaul; do not translate it as trainee Potential.",
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
    _upsert(terms, PERFORMANCE_RELEASE, "id")
    if before != json.dumps(community, ensure_ascii=False, sort_keys=True):
        _write(community_path, community)
        changed = True

    reviews_path = repo_root / "glossary" / "terminology_reviews.json"
    reviews = _load(reviews_path, {"schema_version": 1, "decisions": []})
    decisions = reviews.setdefault("decisions", [])
    if not isinstance(decisions, list):
        raise ValueError("review decisions must be a list")
    before = json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    _upsert(decisions, PERFORMANCE_RELEASE_DECISION, "decision_id")
    if before != json.dumps(reviews, ensure_ascii=False, sort_keys=True):
        _write(reviews_path, reviews)
        changed = True
    return changed


def main() -> int:
    print(f"performance_release_hardening_changed={str(harden(ROOT)).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

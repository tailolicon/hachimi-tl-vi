from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

RULE = {
    "id": "source_bridge.umamusume_idol.category128",
    "category": "source_bridge",
    "source_aliases": ["马娘偶像"],
    "preferred": "thần tượng Mã Nương",
    "compact": [],
    "accepted": ["thần tượng Mã Nương"],
    "forbidden": ["thần tượng Uma Musume", "idol Uma Musume"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [["128"]],
    "match_mode": "contains",
    "basis": "zh-CN 马娘 is source-side shorthand for the project player-facing identity Mã Nương in these song-description idol phrases. Keep the whole phrase scoped to text_data category 128; do not promote bare 马娘 as a global alias.",
}

DECISION = {
    "decision_id": "audit.finding.umamusume-idol-source-bridge",
    "source_zh_cn": "马娘偶像",
    "action": "lock",
    "target_vi": "thần tượng Mã Nương",
    "kind": "source_bridge",
    "category": "source_bridge",
    "note": "Whole-phrase bridge for category-128 idol descriptions; bare 马娘 remains intentionally unregistered globally.",
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


def _upsert(rows: list[Any], record: dict[str, Any], id_field: str) -> None:
    record_id = str(record[id_field])
    for index, row in enumerate(rows):
        if isinstance(row, dict) and str(row.get(id_field) or "") == record_id:
            merged = dict(row)
            merged.update(record)
            rows[index] = merged
            return
    rows.append(record)


def harden(repo_root: Path = ROOT) -> bool:
    changed = False
    community_path = repo_root / "glossary" / "ui_community_terms.json"
    community = _load(community_path, {"schema_version": 1, "terms": []})
    before = json.dumps(community, ensure_ascii=False, sort_keys=True)
    _upsert(community.setdefault("terms", []), RULE, "id")
    if before != json.dumps(community, ensure_ascii=False, sort_keys=True):
        _write(community_path, community)
        changed = True

    reviews_path = repo_root / "glossary" / "terminology_reviews.json"
    reviews = _load(reviews_path, {"schema_version": 1, "decisions": []})
    before = json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    _upsert(reviews.setdefault("decisions", []), DECISION, "decision_id")
    if before != json.dumps(reviews, ensure_ascii=False, sort_keys=True):
        _write(reviews_path, reviews)
        changed = True
    return changed


def main() -> int:
    changed = harden(ROOT)
    print(f"umamusume_idol_source_bridge_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

UMAMUSUME_ARCHIVE_TEAM_BUILDING = {
    "id": "system.archive.team_building_619002",
    "category": "system_label",
    "source_aliases": ["赛马娘名鉴"],
    "preferred": "Archive",
    "compact": [],
    "accepted": ["Archive"],
    "forbidden": ["Danh鉴 Uma Musume", "Danh giám Uma Musume", "Uma Musume Catalog"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["localize_dict.json"],
    "key_exact": ["TeamBuilding619002"],
    "match_mode": "contains",
    "basis": "JP ウマ娘名鑑 is localized in current Global-facing documentation as Archive, the collection/record system with Archive Level and Archive Exp. This occurrence belongs to the Aim for the Stars/Team Building event completion message; keep the rule pinned to TeamBuilding619002 rather than generalizing every 名鉴 occurrence.",
}

UMAMUSUME_ARCHIVE_DECISION = {
    "decision_id": "audit.finding.team-building-umamusume-archive",
    "source_zh_cn": "赛马娘名鉴",
    "action": "lock",
    "target_vi": "Archive",
    "kind": "system_label",
    "category": "system_label",
    "note": "Use current Global-facing Archive terminology for JP ウマ娘名鑑 in the proven TeamBuilding619002 event message; canonical matching remains item-scoped.",
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
    _upsert(community.setdefault("terms", []), UMAMUSUME_ARCHIVE_TEAM_BUILDING, "id")
    if before != json.dumps(community, ensure_ascii=False, sort_keys=True):
        _write(community_path, community)
        changed = True

    reviews_path = repo_root / "glossary" / "terminology_reviews.json"
    reviews = _load(reviews_path, {"schema_version": 1, "decisions": []})
    before = json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    _upsert(reviews.setdefault("decisions", []), UMAMUSUME_ARCHIVE_DECISION, "decision_id")
    if before != json.dumps(reviews, ensure_ascii=False, sort_keys=True):
        _write(reviews_path, reviews)
        changed = True

    return changed


def main() -> int:
    changed = harden(ROOT)
    print(f"umamusume_archive_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

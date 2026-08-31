from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

TRACEN_KEN = {
    "id": "scenario.tracen_ken.text120",
    "category": "scenario",
    "source_aliases": ["特雷森轩"],
    "preferred": "Tracen-ken",
    "compact": [],
    "accepted": ["Tracen-ken"],
    "forbidden": ["特雷森轩", "Tracen Ken", "Tracen Pavilion"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [["120"]],
    "match_mode": "contains",
    "basis": "Named ramen establishment/scenario label corresponding to JP トレセン軒. Current English community scenario references consistently use Tracen-ken. Scope is restricted to text_data category 120 scenario-summary prose so unrelated Tracen Academy strings are unaffected.",
}

TRACEN_KEN_DECISION = {
    "decision_id": "audit.finding.scenario-tracen-ken",
    "source_zh_cn": "特雷森轩",
    "action": "lock",
    "target_vi": "Tracen-ken",
    "kind": "system_label",
    "category": "scenario",
    "note": "Verified against JP トレセン軒 and current English community scenario naming. Use Tracen-ken for the named establishment/scenario; canonical matching remains category-120 scoped.",
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
    _upsert(community.setdefault("terms", []), TRACEN_KEN, "id")
    if before != json.dumps(community, ensure_ascii=False, sort_keys=True):
        _write(community_path, community)
        changed = True

    reviews_path = repo_root / "glossary" / "terminology_reviews.json"
    reviews = _load(reviews_path, {"schema_version": 1, "decisions": []})
    before = json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    _upsert(reviews.setdefault("decisions", []), TRACEN_KEN_DECISION, "decision_id")
    if before != json.dumps(reviews, ensure_ascii=False, sort_keys=True):
        _write(reviews_path, reviews)
        changed = True
    return changed


def main() -> int:
    changed = harden(ROOT)
    print(f"tracen_ken_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

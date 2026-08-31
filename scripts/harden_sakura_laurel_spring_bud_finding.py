from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

SPRING_BUD = {
    "id": "condition.sakura_laurel.spring_bud_awaiting_spring",
    "category": "condition",
    "source_aliases": ["待春之蕾"],
    "preferred": "Flower Bud Awaiting Spring",
    "compact": [],
    "accepted": ["Flower Bud Awaiting Spring"],
    "forbidden": ["Nụ hoa chờ xuân"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [["142"]],
    "match_mode": "exact",
    "basis": "Verified Sakura Laurel Career Condition identity: zh-CN 待春之蕾 maps to JP 春待つ蕾. JP guides show the Condition is applied after Make Debut and remains during her early Career; a public JP condition translation table independently places 春待つ蕾 immediately after 英雄の光輝, matching the source-table ordering. Sakura Laurel is not yet released on Global, so use a direct English player-facing rendering and keep the rule confined to the Condition-name table.",
}

SPRING_BUD_DECISION = {
    "decision_id": "audit.finding.condition-sakura-laurel-spring-bud",
    "source_zh_cn": "待春之蕾",
    "action": "lock",
    "target_vi": "Flower Bud Awaiting Spring",
    "kind": "condition",
    "category": "condition",
    "note": "Verified as JP 春待つ蕾, Sakura Laurel's early-Career Condition after Make Debut. Direct English rendering is used because Sakura Laurel is not yet released on Global.",
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
    _upsert(community.setdefault("terms", []), SPRING_BUD, "id")
    if before != json.dumps(community, ensure_ascii=False, sort_keys=True):
        _write(community_path, community)
        changed = True

    reviews_path = repo_root / "glossary" / "terminology_reviews.json"
    reviews = _load(reviews_path, {"schema_version": 1, "decisions": []})
    before = json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    _upsert(reviews.setdefault("decisions", []), SPRING_BUD_DECISION, "decision_id")
    if before != json.dumps(reviews, ensure_ascii=False, sort_keys=True):
        _write(reviews_path, reviews)
        changed = True
    return changed


def main() -> int:
    changed = harden(ROOT)
    print(f"sakura_laurel_spring_bud_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

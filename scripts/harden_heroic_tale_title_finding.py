from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

HEROIC_TALE_TITLE = {
    "id": "event.league_of_heroes.heroic_tale_title",
    "category": "event",
    "source_aliases": ["英雄奇谭"],
    "preferred": "Anh Hùng Kỳ Đàm",
    "compact": [],
    "accepted": ["Anh Hùng Kỳ Đàm"],
    "forbidden": ["Heroic Tale"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["localize_dict.json"],
    "key_prefixes": ["Heroes511"],
    "match_mode": "contains",
    "basis": "League of Heroes event-limited title label. Existing reviewed corpus and generated regressions consistently use Anh Hùng Kỳ Đàm across the Heroes511 UI family; scope is restricted to that family so unrelated narrative uses of 英雄奇谭 are unaffected.",
}

HEROIC_TALE_DECISION = {
    "decision_id": "audit.finding.league-of-heroes-heroic-tale-title",
    "source_zh_cn": "英雄奇谭",
    "action": "lock",
    "target_vi": "Anh Hùng Kỳ Đàm",
    "kind": "system_label",
    "category": "event",
    "note": "Resolve the split rendering in League of Heroes title UI to the already dominant reviewed Vietnamese label Anh Hùng Kỳ Đàm. Keep the canonical rule scoped to localize_dict Heroes511* keys.",
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
    _upsert(terms, HEROIC_TALE_TITLE, id_field="id")
    if before != json.dumps(community, ensure_ascii=False, sort_keys=True):
        _write(community_path, community)
        changed = True

    reviews_path = repo_root / "glossary" / "terminology_reviews.json"
    reviews = _load(reviews_path, {"schema_version": 1, "decisions": []})
    decisions = reviews.setdefault("decisions", [])
    if not isinstance(decisions, list):
        raise ValueError("glossary/terminology_reviews.json decisions must be a list")
    before = json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    _upsert(decisions, HEROIC_TALE_DECISION, id_field="decision_id")
    if before != json.dumps(reviews, ensure_ascii=False, sort_keys=True):
        _write(reviews_path, reviews)
        changed = True

    return changed


def main() -> int:
    changed = harden(ROOT)
    print(f"heroic_tale_title_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

SENIOR_AUTUMN_TRIPLE_CROWN = {
    "id": "achievement.senior_autumn_triple_crown",
    "category": "achievement",
    "source_aliases": ["秋古马三冠"],
    "preferred": "Senior Autumn Triple Crown",
    "compact": [],
    "accepted": ["Senior Autumn Triple Crown"],
    "forbidden": ["Tam quan Cổ mã Mùa thu", "Tam quán Cổ mã Mùa thu", "Autumn Senior Triple Crown"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "match_mode": "contains",
    "basis": "Recurring player-facing autumn senior Triple Crown achievement label. The live finding occurs both as a standalone label and inside the compound 秋古马三冠赛马娘, so keep the rule scoped to text_data_dict.json while allowing contains matching. Preserve the established English achievement identity Senior Autumn Triple Crown rather than the existing mixed Vietnamese calque.",
}

SENIOR_AUTUMN_TRIPLE_CROWN_DECISION = {
    "decision_id": "audit.finding.senior-autumn-triple-crown",
    "source_zh_cn": "秋古马三冠",
    "action": "lock",
    "target_vi": "Senior Autumn Triple Crown",
    "kind": "system_label",
    "category": "achievement",
    "note": "Canonical player-facing autumn senior Triple Crown label; scoped to text_data_dict.json so the embedded compound title resolves without global alias leakage.",
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
    _upsert(terms, SENIOR_AUTUMN_TRIPLE_CROWN, id_field="id")
    if before != json.dumps(community, ensure_ascii=False, sort_keys=True):
        _write(community_path, community)
        changed = True

    reviews_path = repo_root / "glossary" / "terminology_reviews.json"
    reviews = _load(reviews_path, {"schema_version": 1, "decisions": []})
    decisions = reviews.setdefault("decisions", [])
    if not isinstance(decisions, list):
        raise ValueError("glossary/terminology_reviews.json decisions must be a list")
    before = json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    _upsert(decisions, SENIOR_AUTUMN_TRIPLE_CROWN_DECISION, id_field="decision_id")
    if before != json.dumps(reviews, ensure_ascii=False, sort_keys=True):
        _write(reviews_path, reviews)
        changed = True
    return changed


def main() -> int:
    changed = harden(ROOT)
    print(f"senior_autumn_triple_crown_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

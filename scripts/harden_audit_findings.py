from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

NIGHT_OWL_REFERENCE_VARIANT = {
    "id": "common.condition.night_owl.reference_variant",
    "category": "condition",
    "source_aliases": ["熬夜倾向"],
    "preferred": "Night Owl",
    "compact": [],
    "accepted": ["Night Owl"],
    "forbidden": ["Xu hướng thức khuya", "Thức khuya"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [["143"]],
    "match_mode": "contains",
    "basis": "Named Night Owl Condition reference variant found during retrospective audit; scoped to text_data category 143 so ordinary prose about staying up late is not canonicalized.",
}

JUNIOR_MAKE_DEBUT = {
    "id": "race.junior_make_debut.singlemode619001",
    "category": "race",
    "source_aliases": ["新马级出道赛"],
    "preferred": "Junior Make Debut",
    "compact": [],
    "accepted": ["Junior Make Debut"],
    "forbidden": ["tân mã", "Tân mã", "giải ra mắt cấp Tân mã", "Giải ra mắt cấp Tân mã"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["localize_dict.json"],
    "key_exact": ["SingleMode619001"],
    "match_mode": "contains",
    "basis": "Established English player-facing name for the first Career race objective. The source alias is scoped to the proven SingleMode619001 slot so generic debut prose is unaffected.",
}

JUNIOR_MAKE_DEBUT_DECISION = {
    "decision_id": "audit.finding.junior-make-debut",
    "source_zh_cn": "新马级出道赛",
    "action": "lock",
    "target_vi": "Junior Make Debut",
    "kind": "race",
    "category": "race",
    "note": "Established player-facing English race label for the initial Career objective; canonical matching itself remains item-scoped through race.junior_make_debut.singlemode619001.",
}


def _load(path: Path, default: dict[str, Any] | None = None) -> dict[str, Any]:
    if not path.exists():
        return dict(default or {})
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _upsert(items: list[Any], record: dict[str, Any], *, id_field: str = "id") -> None:
    record_id = str(record[id_field])
    for index, item in enumerate(items):
        if isinstance(item, dict) and str(item.get(id_field) or "") == record_id:
            merged = dict(item)
            merged.update(record)
            items[index] = merged
            return
    items.append(record)


def harden(repo_root: Path = ROOT) -> bool:
    changed = False

    community_path = repo_root / "glossary" / "ui_community_terms.json"
    community = _load(community_path, {"schema_version": 1, "terms": []})
    before = json.dumps(community, ensure_ascii=False, sort_keys=True)
    terms = community.setdefault("terms", [])
    if not isinstance(terms, list):
        raise ValueError("glossary/ui_community_terms.json terms must be a list")
    _upsert(terms, NIGHT_OWL_REFERENCE_VARIANT)
    _upsert(terms, JUNIOR_MAKE_DEBUT)
    if before != json.dumps(community, ensure_ascii=False, sort_keys=True):
        _write(community_path, community)
        changed = True

    reviews_path = repo_root / "glossary" / "terminology_reviews.json"
    reviews = _load(reviews_path, {"schema_version": 1, "decisions": []})
    before = json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    decisions = reviews.setdefault("decisions", [])
    if not isinstance(decisions, list):
        raise ValueError("glossary/terminology_reviews.json decisions must be a list")
    _upsert(decisions, JUNIOR_MAKE_DEBUT_DECISION, id_field="decision_id")
    if before != json.dumps(reviews, ensure_ascii=False, sort_keys=True):
        _write(reviews_path, reviews)
        changed = True

    return changed


def main() -> int:
    changed = harden(ROOT)
    print(f"audit_finding_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

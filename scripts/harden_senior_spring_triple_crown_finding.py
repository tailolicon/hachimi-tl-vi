from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

SENIOR_SPRING_TRIPLE_CROWN = {
    "id": "achievement.senior_spring_triple_crown",
    "category": "achievement",
    "source_aliases": ["春古马三冠"],
    "preferred": "Senior Spring Triple Crown",
    "compact": [],
    "accepted": ["Senior Spring Triple Crown"],
    "forbidden": ["Tam quán mùa xuân Hạng Senior", "Spring Senior Triple Crown"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [["111"]],
    "match_mode": "exact",
    "basis": "Player-facing Triple Crown achievement corresponding to JP 春シニア三冠. Current Global English guides consistently use Senior Spring Triple Crown for the Osaka Hai, Tenno Sho (Spring), and Takarazuka Kinen set; preserve that established English identity rather than a Vietnamese calque.",
}

SENIOR_SPRING_TRIPLE_CROWN_DECISION = {
    "decision_id": "audit.finding.senior-spring-triple-crown",
    "source_zh_cn": "春古马三冠",
    "action": "lock",
    "target_vi": "Senior Spring Triple Crown",
    "kind": "system_label",
    "category": "achievement",
    "note": "Canonical player-facing Triple Crown label for JP 春シニア三冠.",
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
    _upsert(terms, SENIOR_SPRING_TRIPLE_CROWN, id_field="id")
    if before != json.dumps(community, ensure_ascii=False, sort_keys=True):
        _write(community_path, community)
        changed = True

    reviews_path = repo_root / "glossary" / "terminology_reviews.json"
    reviews = _load(reviews_path, {"schema_version": 1, "decisions": []})
    decisions = reviews.setdefault("decisions", [])
    if not isinstance(decisions, list):
        raise ValueError("glossary/terminology_reviews.json decisions must be a list")
    before = json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    _upsert(decisions, SENIOR_SPRING_TRIPLE_CROWN_DECISION, id_field="decision_id")
    if before != json.dumps(reviews, ensure_ascii=False, sort_keys=True):
        _write(reviews_path, reviews)
        changed = True
    return changed


def main() -> int:
    changed = harden(ROOT)
    print(f"senior_spring_triple_crown_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

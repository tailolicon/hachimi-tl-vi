from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

TRAINEE_TEXT_DATA = {
    "id": "career.ui.trainee.text_data",
    "category": "career_ui",
    "source_aliases": ["育成赛马娘"],
    "preferred": "Trainee",
    "compact": [],
    "accepted": ["Trainee"],
    "forbidden": ["Uma Musume huấn luyện", "Uma Musume Huấn luyện", "Mã Nương huấn luyện"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [],
    "match_mode": "contains",
    "basis": "The repository already defines the full compound 育成赛马娘 / 育成ウマ娘 as the player-facing Trainee concept and explicitly excludes it from generic Umamusume matching. Extend that same full-compound identity to text_data descriptions. This does not map bare 育成 or bare 赛马娘 and therefore avoids the ambiguity that required the original localize_dict key scoping.",
}

TRAINEE_TEXT_DATA_DECISION = {
    "decision_id": "audit.finding.trainee-text-data",
    "source_zh_cn": "育成赛马娘",
    "action": "lock",
    "target_vi": "Trainee",
    "kind": "system_label",
    "category": "career_ui",
    "note": "Reuse the already-established full-compound Trainee identity in text_data; bare 育成 and bare 赛马娘 remain outside this lock.",
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
    _upsert(terms, TRAINEE_TEXT_DATA, id_field="id")
    if before != json.dumps(community, ensure_ascii=False, sort_keys=True):
        _write(community_path, community)
        changed = True

    reviews_path = repo_root / "glossary" / "terminology_reviews.json"
    reviews = _load(reviews_path, {"schema_version": 1, "decisions": []})
    decisions = reviews.setdefault("decisions", [])
    if not isinstance(decisions, list):
        raise ValueError("glossary/terminology_reviews.json decisions must be a list")
    before = json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    _upsert(decisions, TRAINEE_TEXT_DATA_DECISION, id_field="decision_id")
    if before != json.dumps(reviews, ensure_ascii=False, sort_keys=True):
        _write(reviews_path, reviews)
        changed = True
    return changed


def main() -> int:
    changed = harden(ROOT)
    print(f"trainee_text_data_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

WEEKEND_CHALLENGE = {
    "id": "event.monthly_match.weekend_challenge",
    "category": "event",
    "source_aliases": ["周末挑战"],
    "preferred": "Weekend Challenge",
    "compact": [],
    "accepted": ["Weekend Challenge"],
    "forbidden": ["Thử thách cuối tuần"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["localize_dict.json"],
    "key_exact": ["RatingRace600015"],
    "match_mode": "contains",
    "basis": "Named Monthly Match feature label. Current English community/reference usage calls this phase Weekend Challenge; keep the rule narrowly scoped to the proven RatingRace600015 UI slot so generic weekend-challenge prose is unaffected.",
}

WEEKEND_CHALLENGE_DECISION = {
    "decision_id": "audit.finding.weekend-challenge",
    "source_zh_cn": "周末挑战",
    "action": "lock",
    "target_vi": "Weekend Challenge",
    "kind": "system_label",
    "category": "event",
    "note": "Verified named Monthly Match feature label. The canonical rule remains narrowly scoped to localize_dict RatingRace600015 so generic weekend prose is unaffected.",
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
    _upsert(terms, WEEKEND_CHALLENGE, id_field="id")
    if before != json.dumps(community, ensure_ascii=False, sort_keys=True):
        _write(community_path, community)
        changed = True

    reviews_path = repo_root / "glossary" / "terminology_reviews.json"
    reviews = _load(reviews_path, {"schema_version": 1, "decisions": []})
    decisions = reviews.setdefault("decisions", [])
    if not isinstance(decisions, list):
        raise ValueError("glossary/terminology_reviews.json decisions must be a list")
    before = json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    _upsert(decisions, WEEKEND_CHALLENGE_DECISION, id_field="decision_id")
    if before != json.dumps(reviews, ensure_ascii=False, sort_keys=True):
        _write(reviews_path, reviews)
        changed = True

    return changed


def main() -> int:
    changed = harden(ROOT)
    print(f"weekend_challenge_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

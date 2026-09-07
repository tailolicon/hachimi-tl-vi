from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TERM_ID = "scenario.great_food_festival.cooking_points"
DECISION_ID = "audit.finding.great-food-festival-cooking-points"
FINDING_ID = "cf-9c3a9ad76cae6fe6"
ALIAS = "料理Pt"
TARGET = "Cooking Points"

TERM = {
    "id": TERM_ID,
    "category": "system_label",
    "source_aliases": [ALIAS],
    "preferred": TARGET,
    "compact": [TARGET],
    "accepted": [TARGET],
    "forbidden": ["Pt Món ăn", "Pt Nấu ăn", "Điểm nấu ăn"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["localize_dict.json"],
    "match_mode": "contains",
    "basis": (
        "Great Food Festival uses the recurring JP system label お料理Pt/料理Pt for the scenario's "
        "cooking score. Established English scenario references consistently call the same mechanic "
        "Cooking Points. Bridge only the explicit 料理Pt alias in localize_dict.json; generic cooking "
        "prose remains unaffected."
    ),
}

REVIEW = {
    "decision_id": DECISION_ID,
    "source_zh_cn": ALIAS,
    "action": "lock",
    "target_vi": TARGET,
    "kind": "system_label",
    "category": "scenario",
    "invalidation_scope": "item",
    "source_paths": ["localize_dict.json"],
    "match_mode": "contains",
    "note": (
        "料理Pt is the reusable Great Food Festival cooking-score label. Canonicalize it as "
        "Cooking Points instead of alternating Pt Món ăn / Pt Nấu ăn renderings."
    ),
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


def _upsert(rows: list[Any], key: str, value: str, payload: dict[str, Any]) -> None:
    for index, item in enumerate(rows):
        if isinstance(item, dict) and item.get(key) == value:
            merged = dict(item)
            merged.update(payload)
            rows[index] = merged
            return
    rows.append(dict(payload))


def harden(repo_root: Path = ROOT) -> bool:
    changed = False

    community_path = repo_root / "glossary" / "ui_community_terms.json"
    community = _load(community_path)
    terms = community.get("terms")
    if not isinstance(terms, list):
        raise ValueError("glossary/ui_community_terms.json terms must be a list")
    before = json.dumps(community, ensure_ascii=False, sort_keys=True)
    _upsert(terms, "id", TERM_ID, TERM)
    if before != json.dumps(community, ensure_ascii=False, sort_keys=True):
        _write(community_path, community)
        changed = True

    reviews_path = repo_root / "glossary" / "terminology_reviews.json"
    reviews = _load(reviews_path, {"schema_version": 1, "decisions": []})
    decisions = reviews.setdefault("decisions", [])
    if not isinstance(decisions, list):
        raise ValueError("glossary/terminology_reviews.json decisions must be a list")
    before = json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    _upsert(decisions, "decision_id", DECISION_ID, REVIEW)
    if before != json.dumps(reviews, ensure_ascii=False, sort_keys=True):
        _write(reviews_path, reviews)
        changed = True

    findings_path = repo_root / "glossary" / "canonical_findings.json"
    findings = _load(findings_path, {"schema_version": 1, "findings": []})
    before = json.dumps(findings, ensure_ascii=False, sort_keys=True)
    matched = False
    for finding in findings.get("findings", []):
        if not isinstance(finding, dict) or finding.get("finding_id") != FINDING_ID:
            continue
        matched = True
        suggestions = [str(value) for value in finding.get("suggested_targets_vi", []) if str(value)]
        if TARGET not in suggestions:
            suggestions.append(TARGET)
        finding["suggested_targets_vi"] = suggestions
        break
    if not matched:
        raise ValueError(f"missing canonical finding {FINDING_ID}")
    if before != json.dumps(findings, ensure_ascii=False, sort_keys=True):
        _write(findings_path, findings)
        changed = True

    return changed


def main() -> int:
    changed = harden(ROOT)
    print(f"cooking_points_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

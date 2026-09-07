from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FINDING_ID = "cf-61d905f4d2327086"
BASE_TERM_ID = "event.league_of_heroes"
BRIDGE_TERM_ID = "event.league_of_heroes.hero_league_alias"
DECISION_ID = "audit.finding.league-of-heroes-hero-league-alias"
ALIAS = "英雄联赛"
TARGET = "League of Heroes"

BRIDGE_TERM = {
    "id": BRIDGE_TERM_ID,
    "category": "event",
    "source_aliases": [ALIAS],
    "preferred": TARGET,
    "compact": ["LoH"],
    "accepted": [TARGET],
    "forbidden": ["Hero League", "Liên minh Anh hùng"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["localize_dict.json"],
    "match_mode": "contains",
    "basis": (
        "Worker evidence uses zh-CN 英雄联赛 for the same named event already canonicalized as "
        "League of Heroes. Keep the established global event rule unchanged and bridge this alias "
        "only within localize_dict.json so generic 英雄/联赛 prose cannot inherit the event name."
    ),
}

REVIEW_DECISION = {
    "decision_id": DECISION_ID,
    "source_zh_cn": ALIAS,
    "action": "lock",
    "target_vi": TARGET,
    "kind": "event_name",
    "category": "event",
    "invalidation_scope": "item",
    "source_paths": ["localize_dict.json"],
    "match_mode": "contains",
    "note": (
        "英雄联赛 is the worker-reported zh-CN alias for the named League of Heroes event. "
        "Scope the bridge to localize_dict.json; the existing event.league_of_heroes rule remains the canonical identity."
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
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def _replace(items: list[Any], record: dict[str, Any], id_field: str) -> None:
    record_id = str(record[id_field])
    for index, item in enumerate(items):
        if isinstance(item, dict) and str(item.get(id_field) or "") == record_id:
            items[index] = dict(record)
            return
    items.append(dict(record))


def harden(repo_root: Path = ROOT) -> bool:
    changed = False

    community_path = repo_root / "glossary" / "ui_community_terms.json"
    community = _load(community_path)
    terms = community.get("terms")
    if not isinstance(terms, list):
        raise ValueError("glossary/ui_community_terms.json terms must be a list")
    if not any(isinstance(item, dict) and item.get("id") == BASE_TERM_ID for item in terms):
        raise ValueError(f"missing canonical base term {BASE_TERM_ID}")
    before = json.dumps(community, ensure_ascii=False, sort_keys=True)
    _replace(terms, BRIDGE_TERM, "id")
    if before != json.dumps(community, ensure_ascii=False, sort_keys=True):
        _write(community_path, community)
        changed = True

    reviews_path = repo_root / "glossary" / "terminology_reviews.json"
    reviews = _load(reviews_path, {"schema_version": 1, "decisions": []})
    decisions = reviews.setdefault("decisions", [])
    if not isinstance(decisions, list):
        raise ValueError("glossary/terminology_reviews.json decisions must be a list")
    before = json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    _replace(decisions, REVIEW_DECISION, "decision_id")
    if before != json.dumps(reviews, ensure_ascii=False, sort_keys=True):
        _write(reviews_path, reviews)
        changed = True

    findings_path = repo_root / "glossary" / "canonical_findings.json"
    findings = _load(findings_path, {"schema_version": 1, "findings": []})
    before = json.dumps(findings, ensure_ascii=False, sort_keys=True)
    for finding in findings.get("findings", []):
        if not isinstance(finding, dict) or finding.get("finding_id") != FINDING_ID:
            continue
        suggestions = [str(value) for value in finding.get("suggested_targets_vi", []) if str(value)]
        if TARGET not in suggestions:
            suggestions.append(TARGET)
        finding["suggested_targets_vi"] = suggestions
        break
    if before != json.dumps(findings, ensure_ascii=False, sort_keys=True):
        _write(findings_path, findings)
        changed = True

    return changed


def main() -> int:
    print(f"league_of_heroes_alias_hardening_changed={str(harden(ROOT)).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

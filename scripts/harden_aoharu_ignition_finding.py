from __future__ import annotations

"""Canonicalize the Aoharu Ignition (アオハル点火) Skill-title family.

The pinned zh-CN source uses 点燃青春 for アオハル点火. Historical review
context conflated its + variants with the distinct アオハル燃焼 / 燃烧青春
family, and a later legacy review lock attempted to preserve the Global family
name Ignited Spirit. Individual Skill names in this repository are localized,
so keep one Vietnamese canonical family and remove every conflicting family-level
legacy rule/lock while leaving exact individual Skill locks untouched.
"""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FINDING_ID = "cf-d3dd61a3ce1f7dd6"
PREFERRED = "Thắp lửa thanh xuân"
LEGACY_CONFLICT_ID = "skill.aoharu.ignited_spirit.family"
LEGACY_REVIEW_DECISION_ID = "audit.finding.aoharu-ignited-spirit-family"
LEGACY_LOCKED_TERM_ID = "reviewed.skill_name.151234fc3eb9"

AOHARU_IGNITION = {
    "id": "skill.aoharu_ignition.family",
    "category": "skill_name",
    "source_aliases": ["点燃青春"],
    "preferred": PREFERRED,
    "compact": [],
    "accepted": [PREFERRED],
    "forbidden": ["Bùng cháy thanh xuân", "Ignited Spirit"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [["147"]],
    "match_mode": "contains",
    "basis": (
        "Verified JP identity: zh-CN 点燃青春 is アオハル点火 (Aoharu Ignition), "
        "distinct from アオハル燃焼 / 燃烧青春. Individual Skill names are localized "
        "under repository policy, so preserve the established Vietnamese ignition-family "
        "base Thắp lửa thanh xuân and reject both combustion-family wording and the "
        "conflicting keep-English legacy family lock only for 点燃青春 Skill titles in category 147."
    ),
}


def _load(path: Path) -> dict[str, Any]:
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


def _remove_by_id(items: list[Any], *, id_field: str, record_id: str) -> None:
    items[:] = [
        item
        for item in items
        if not (isinstance(item, dict) and str(item.get(id_field) or "") == record_id)
    ]


def harden(repo_root: Path = ROOT) -> bool:
    changed = False

    community_path = repo_root / "glossary" / "ui_community_terms.json"
    community = _load(community_path)
    terms = community.get("terms")
    if not isinstance(terms, list):
        raise ValueError("glossary/ui_community_terms.json terms must be a list")
    before = json.dumps(community, ensure_ascii=False, sort_keys=True)
    _remove_by_id(terms, id_field="id", record_id=LEGACY_CONFLICT_ID)
    _upsert(terms, AOHARU_IGNITION, id_field="id")
    if before != json.dumps(community, ensure_ascii=False, sort_keys=True):
        _write(community_path, community)
        changed = True

    reviews_path = repo_root / "glossary" / "terminology_reviews.json"
    reviews = _load(reviews_path)
    decisions = reviews.get("decisions")
    if not isinstance(decisions, list):
        raise ValueError("glossary/terminology_reviews.json decisions must be a list")
    before = json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    _remove_by_id(decisions, id_field="decision_id", record_id=LEGACY_REVIEW_DECISION_ID)
    if before != json.dumps(reviews, ensure_ascii=False, sort_keys=True):
        _write(reviews_path, reviews)
        changed = True

    registry_path = repo_root / "glossary" / "term_registry.json"
    registry = _load(registry_path)
    registry_terms = registry.get("terms")
    if not isinstance(registry_terms, list):
        raise ValueError("glossary/term_registry.json terms must be a list")
    before = json.dumps(registry, ensure_ascii=False, sort_keys=True)
    _remove_by_id(registry_terms, id_field="id", record_id=LEGACY_LOCKED_TERM_ID)
    if before != json.dumps(registry, ensure_ascii=False, sort_keys=True):
        _write(registry_path, registry)
        changed = True

    findings_path = repo_root / "glossary" / "canonical_findings.json"
    findings = _load(findings_path)
    before = json.dumps(findings, ensure_ascii=False, sort_keys=True)
    matched = False
    for finding in findings.get("findings", []):
        if not isinstance(finding, dict) or finding.get("finding_id") != FINDING_ID:
            continue
        matched = True
        suggestions = [str(value) for value in finding.get("suggested_targets_vi", []) if str(value)]
        suggestions = [value for value in suggestions if value != "Ignited Spirit"]
        if PREFERRED not in suggestions:
            suggestions.append(PREFERRED)
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
    print(f"aoharu_ignition_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

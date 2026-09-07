from __future__ import annotations

"""Resolve Mejiro Palmer's Keep Pushing Ahead title inside inheritance descriptions."""

import json
from pathlib import Path
from typing import Any

try:
    from scripts.harden_bucchigiri_road_finding import PREFERRED as TARGET, SOURCE_JA, SOURCE_ZH
except ModuleNotFoundError:  # direct execution: python scripts/harden_*_finding.py
    from harden_bucchigiri_road_finding import PREFERRED as TARGET, SOURCE_JA, SOURCE_ZH

ROOT = Path(__file__).resolve().parents[1]
FINDING_ID = "cf-70b5883f9b7068e2"
TERM_ID = "skill.mejiro_palmer.keep_pushing_ahead.inheritance"
DECISION_ID = "audit.finding.skill-mejiro-palmer-keep-pushing-ahead-inheritance"
INHERITANCE_PREFIXES = [["172"]]

RULE = {
    "id": TERM_ID,
    "category": "skill_name",
    "source_aliases": [SOURCE_ZH],
    "preferred": TARGET,
    "compact": [],
    "accepted": [TARGET],
    "forbidden": ["Con đường độc tôn"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": INHERITANCE_PREFIXES,
    "match_mode": "contains",
    "basis": (
        "The already verified Skill 冠绝之路 / ぶっちぎりロード is canonically Keep Pushing Ahead. "
        "Category 172 inheritance descriptions embed that exact Skill alias inside longer factor prose, "
        "so reuse the same canonical title only in inheritance rows rather than widening the standalone "
        "category-147 exact matcher."
    ),
}

DECISION = {
    "decision_id": DECISION_ID,
    "source_zh_cn": SOURCE_ZH,
    "action": "lock",
    "target_vi": TARGET,
    "kind": "proper_name",
    "category": "skill_name",
    "ja": [SOURCE_JA],
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": INHERITANCE_PREFIXES,
    "match_mode": "contains",
    "note": (
        "Inheritance category 172 embeds Mejiro Palmer's already verified unique Skill 冠绝之路; "
        "reuse Keep Pushing Ahead in that narrow scope."
    ),
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
    _upsert(community.setdefault("terms", []), RULE, "id")
    if before != json.dumps(community, ensure_ascii=False, sort_keys=True):
        _write(community_path, community)
        changed = True

    reviews_path = repo_root / "glossary" / "terminology_reviews.json"
    reviews = _load(reviews_path, {"schema_version": 1, "decisions": []})
    before = json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    _upsert(reviews.setdefault("decisions", []), DECISION, "decision_id")
    if before != json.dumps(reviews, ensure_ascii=False, sort_keys=True):
        _write(reviews_path, reviews)
        changed = True

    findings_path = repo_root / "glossary" / "canonical_findings.json"
    findings = _load(findings_path, {"schema_version": 1, "findings": []})
    before = json.dumps(findings, ensure_ascii=False, sort_keys=True)
    matched = False
    for finding in findings.get("findings", []):
        if not isinstance(finding, dict) or str(finding.get("finding_id") or "") != FINDING_ID:
            continue
        matched = True
        suggestions = [str(value) for value in finding.get("suggested_targets_vi", []) if str(value)]
        if TARGET not in suggestions:
            suggestions.append(TARGET)
        finding["suggested_targets_vi"] = suggestions
        break
    if not matched:
        raise ValueError(f"missing canonical finding: {FINDING_ID}")
    if before != json.dumps(findings, ensure_ascii=False, sort_keys=True):
        _write(findings_path, findings)
        changed = True

    return changed


def main() -> int:
    changed = harden(ROOT)
    print(f"bucchigiri_road_inheritance_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

"""Resolve the 点燃青春 family to the Global Ignited Spirit skill names.

zh-CN 点燃青春 is the localized identity of JP アオハル点火, the normal
Unity Cup skill family.  Global player-facing names are Ignited Spirit
SPD/STA/PWR/GUTS/WIT.  Keep the reusable family rule confined to skill titles
(text_data category 147) and lock each full title exactly so ordinary prose
containing 青春 is unaffected.
"""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FINDING_ID = "cf-d3dd61a3ce1f7dd6"

FAMILY_RULE = {
    "id": "skill.aoharu.ignited_spirit.family",
    "category": "skill_name",
    "source_aliases": ["点燃青春"],
    "preferred": "Ignited Spirit",
    "accepted": ["Ignited Spirit"],
    "compact": [],
    "forbidden": ["Thắp lửa thanh xuân"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [["147"]],
    "match_mode": "contains",
    "basis": "JP アオハル点火 is the Unity Cup/Aoharu normal skill family; Global uses Ignited Spirit. Scope is limited to Skill-title category 147.",
}

VARIANTS = (
    ("点燃青春・速", "Ignited Spirit SPD", "アオハル点火・速"),
    ("点燃青春・体", "Ignited Spirit STA", "アオハル点火・体"),
    ("点燃青春・力", "Ignited Spirit PWR", "アオハル点火・力"),
    ("点燃青春・根", "Ignited Spirit GUTS", "アオハル点火・根"),
    ("点燃青春・智", "Ignited Spirit WIT", "アオハル点火・賢"),
)


def _load(path: Path, default: dict[str, Any] | None = None) -> dict[str, Any]:
    if not path.exists():
        return dict(default or {})
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
    items.append(record)


def harden(repo_root: Path = ROOT) -> bool:
    changed = False

    community_path = repo_root / "glossary" / "ui_community_terms.json"
    community = _load(community_path, {"schema_version": 1, "terms": []})
    before = json.dumps(community, ensure_ascii=False, sort_keys=True)
    _upsert(community.setdefault("terms", []), FAMILY_RULE, "id")
    if before != json.dumps(community, ensure_ascii=False, sort_keys=True):
        _write(community_path, community)
        changed = True

    reviews_path = repo_root / "glossary" / "terminology_reviews.json"
    reviews = _load(reviews_path, {"schema_version": 1, "decisions": []})
    before = json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    decisions = reviews.setdefault("decisions", [])

    family_decision = {
        "decision_id": "audit.finding.aoharu-ignited-spirit-family",
        "source_zh_cn": "点燃青春",
        "action": "lock",
        "target_vi": "Ignited Spirit",
        "kind": "skill_name",
        "category": "skill_name",
        "invalidation_scope": "item",
        "source_paths": ["text_data_dict.json"],
        "json_path_prefixes": [["147"]],
        "match_mode": "contains",
        "note": "Verified identity bridge: zh-CN 点燃青春 = JP アオハル点火; Global family label is Ignited Spirit.",
    }
    _upsert(decisions, family_decision, "decision_id")

    for ordinal, (source, target, jp) in enumerate(VARIANTS, start=1):
        decision = {
            "decision_id": f"audit.finding.aoharu-ignited-spirit-{ordinal}",
            "source_zh_cn": source,
            "action": "lock",
            "target_vi": target,
            "kind": "skill_name",
            "category": "skill_name",
            "ja": [jp],
            "invalidation_scope": "item",
            "source_paths": ["text_data_dict.json"],
            "json_path_prefixes": [["147"]],
            "match_mode": "exact",
            "note": f"Global Unity Cup skill name for JP {jp}; replaces literal zh-CN-derived wording.",
        }
        _upsert(decisions, decision, "decision_id")

    if before != json.dumps(reviews, ensure_ascii=False, sort_keys=True):
        _write(reviews_path, reviews)
        changed = True

    findings_path = repo_root / "glossary" / "canonical_findings.json"
    findings = _load(findings_path, {"schema_version": 1, "findings": []})
    before = json.dumps(findings, ensure_ascii=False, sort_keys=True)
    matched = False
    for finding in findings.get("findings", []):
        if isinstance(finding, dict) and finding.get("finding_id") == FINDING_ID:
            matched = True
            suggestions = [str(value) for value in finding.get("suggested_targets_vi", []) if str(value)]
            if "Ignited Spirit" not in suggestions:
                suggestions.append("Ignited Spirit")
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
    print(f"aoharu_ignited_spirit_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

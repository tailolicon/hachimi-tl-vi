from __future__ import annotations

"""Resolve the 前行 overmatch on 稳步前行 and canonize JP 一歩ずつ前へ."""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FINDING_ID = "cf-df8f8811150b46f9"
LOCKED_TERM_ID = "reviewed.skill_name.321d0fec9832"
SOURCE_ZH = "稳步前行"
SOURCE_JA = "一歩ずつ前へ"
TARGET = "Từng bước tiến lên"
RULE_ID = "skill.one_step_at_a_time"
DECISION_ID = "audit.finding.skill-one-step-at-a-time"

RULE = {
    "id": RULE_ID,
    "category": "skill_name",
    "source_aliases": [SOURCE_ZH],
    "preferred": TARGET,
    "compact": [],
    "accepted": [TARGET],
    "forbidden": ["Tiến bước vững vàng", "Nhắm Tuyến Đầu"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [["147"]],
    "match_mode": "exact",
    "basis": (
        "Pinned locator 47:203362 identifies zh-CN 稳步前行 as JP 一歩ずつ前へ. "
        "The JP title means moving forward one step at a time, so 'Từng bước tiến lên' "
        "preserves the incremental forward-motion identity. This title is distinct from "
        "zh-CN 前行 / JP 前列狙い, whose canonical target is 'Nhắm Tuyến Đầu'."
    ),
}

DECISION = {
    "decision_id": DECISION_ID,
    "source_zh_cn": SOURCE_ZH,
    "action": "lock",
    "target_vi": TARGET,
    "kind": "skill_name",
    "category": "skill_name",
    "ja": [SOURCE_JA],
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [["147"]],
    "match_mode": "exact",
    "note": (
        "Curation evidence verifies locator 47:203362 as JP 一歩ずつ前へ. Keep this "
        "Skill distinct from 前行 / 前列狙い and use the reviewed target 'Từng bước tiến lên'."
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

    registry_path = repo_root / "glossary" / "term_registry.json"
    registry = _load(registry_path)
    before = json.dumps(registry, ensure_ascii=False, sort_keys=True)
    matched = False
    for term in registry.get("terms", []):
        if not isinstance(term, dict) or term.get("id") != LOCKED_TERM_ID:
            continue
        matched = True
        term["match_mode"] = "exact"
        term["invalidation_scope"] = "item"
        term["context_note"] = (
            "前行 is the lossy zh-CN title for JP 前列狙い only when it is the complete "
            "Skill-title source. Do not match the distinct Skill 稳步前行 / JP 一歩ずつ前へ."
        )
        break
    if not matched:
        raise ValueError(f"missing canonical term {LOCKED_TERM_ID}")
    if before != json.dumps(registry, ensure_ascii=False, sort_keys=True):
        _write(registry_path, registry)
        changed = True

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
    found = False
    for finding in findings.get("findings", []):
        if not isinstance(finding, dict) or finding.get("finding_id") != FINDING_ID:
            continue
        found = True
        suggestions = [str(value) for value in finding.get("suggested_targets_vi", []) if str(value)]
        if TARGET not in suggestions:
            suggestions.append(TARGET)
        finding["suggested_targets_vi"] = suggestions
        break
    if not found:
        raise ValueError(f"missing canonical finding {FINDING_ID}")
    if before != json.dumps(findings, ensure_ascii=False, sort_keys=True):
        _write(findings_path, findings)
        changed = True

    return changed


def main() -> int:
    changed = harden(ROOT)
    print(f"one_step_at_a_time_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

"""Canonicalize pinned Skill 101201: JP 無二無三なる一条の路 / zh-CN 一线生路无二亦无三."""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FINDING_ID = "cf-875a4950fbb079e9"
SOURCE_ZH = "一线生路无二亦无三"
SOURCE_JA = "無二無三なる一条の路"
TARGET = "Con Đường Độc Nhất Vô Nhị"
HISTORICAL_TARGET = "Một tia sinh lộ, không hai chẳng ba"

RULE = {
    "id": "skill.muji_musan_naru_ichijo_no_michi.unique_single_path",
    "category": "skill_name",
    "source_aliases": [SOURCE_ZH],
    "preferred": TARGET,
    "compact": [],
    "accepted": [TARGET],
    "forbidden": [HISTORICAL_TARGET],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "match_mode": "exact",
    "basis": (
        "Pinned curation verifies Skill 101201 as Japanese 無二無三なる一条の路. The existing zh-CN bridge "
        "uses a separate wordplay ('a thread of survival, neither two nor three'), while the JP title is "
        "a literary statement of one incomparable path. Use the compact Vietnamese title 'Con Đường Độc "
        "Nhất Vô Nhị' to preserve the JP identity instead of calquing the zh-CN pun."
    ),
}

DECISION = {
    "decision_id": "audit.finding.skill-unique-single-path",
    "source_zh_cn": SOURCE_ZH,
    "action": "lock",
    "target_vi": TARGET,
    "kind": "skill_name",
    "category": "skill_name",
    "ja": [SOURCE_JA],
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "match_mode": "exact",
    "note": (
        "Pinned Skill 101201 verifies JP 無二無三なる一条の路. Resolve the earlier style defer with a compact "
        "Vietnamese title that follows the JP meaning and avoids importing the distinct zh-CN wordplay."
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
        if isinstance(finding, dict) and finding.get("finding_id") == FINDING_ID:
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
    print(f"unique_single_path_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

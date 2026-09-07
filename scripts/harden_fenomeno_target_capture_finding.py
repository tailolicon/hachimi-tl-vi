from __future__ import annotations

"""Canonicalize Fenomeno's JP-only unique Skill 対象捕捉！正義遂行！."""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FINDING_ID = "cf-547f1a03893d2440"
SOURCE_ZH = "捕捉目标！正义执行！"
SOURCE_JA = "対象捕捉！正義遂行！"
TARGET = SOURCE_JA
HISTORICAL_TARGET = "Bắt giữ mục tiêu! Thực thi chính nghĩa!"

RULE = {
    "id": "skill.fenomeno.target_capture_justice.preserve_japanese_title",
    "category": "skill_name",
    "source_aliases": [SOURCE_ZH],
    "preferred": TARGET,
    "compact": [],
    "accepted": [TARGET],
    "forbidden": [HISTORICAL_TARGET],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "match_mode": "contains",
    "basis": (
        "Verified identity: zh-CN 捕捉目标！正义执行！ in Fenomeno Skill/inheritance IDs 11270101-11270103 maps to "
        "JP 対象捕捉！正義遂行！, the JP-only unique Skill of [義心の黒焔] Fenomeno. Preserve the exact Japanese "
        "display title until an official Global title exists instead of retaining the historical zh-CN-derived Vietnamese calque."
    ),
}

DECISION = {
    "decision_id": "audit.finding.skill-fenomeno-target-capture-justice",
    "source_zh_cn": SOURCE_ZH,
    "action": "lock",
    "target_vi": TARGET,
    "kind": "skill_name",
    "category": "skill_name",
    "ja": [SOURCE_JA],
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "match_mode": "contains",
    "note": (
        "Skill/inheritance IDs 11270101-11270103 identify Fenomeno's unique Skill as JP 対象捕捉！正義遂行！. "
        "The Skill remains JP-only, so preserve its exact JP identity rather than inventing an English title or using the old Chinese-derived Vietnamese calque."
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
    print(f"fenomeno_target_capture_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

"""Canonicalize No Reason's unique Skill 知宵欺敵、百戦不殆."""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FINDING_ID = "cf-0fe33e249eca596b"
TITLE_FINDING_ID = "cf-a73e3962c7a5f8a8"
FINDING_IDS = (FINDING_ID, TITLE_FINDING_ID)
SOURCE_ZH = "知宵欺敌 百战不殆"
SOURCE_ZH_COMMA = "知宵欺敌,百战不殆"
SOURCE_ZH_VARIANTS = [SOURCE_ZH, SOURCE_ZH_COMMA]
SOURCE_JA = "知宵欺敵、百戦不殆"
TARGET = "Thấu thời lừa địch, trăm trận không nguy"
HISTORICAL_TITLE_TARGET = "Biết ta biết địch, trăm trận không nguy"

RULE = {
    "id": "skill.no_reason.zhixiao_baizhan",
    "category": "skill_name",
    "source_aliases": SOURCE_ZH_VARIANTS,
    "preferred": TARGET,
    "compact": [],
    "accepted": [TARGET],
    "forbidden": [HISTORICAL_TITLE_TARGET],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "match_mode": "contains",
    "basis": (
        "Japanese sources identify No Reason's unique Skill as 知宵欺敵、百戦不殆. The pinned "
        "zh-CN corpus contains the same Skill identity in two punctuation variants: the "
        "inheritance-factor alias 知宵欺敌 百战不殆 and the category-147 title "
        "知宵欺敌,百战不殆. Both must resolve to the established Vietnamese canonical title "
        "'Thấu thời lừa địch, trăm trận không nguy'. 知宵 is a stylized wording and must not "
        "be normalized into the unrelated stock phrase 'biết ta'; contains scope is retained "
        "because the space-form alias also appears inside longer factor-description strings."
    ),
}

DECISION = {
    "decision_id": "audit.finding.skill-no-reason-zhixiao-baizhan",
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
        "JP-backed identity: No Reason's unique Skill is 知宵欺敵、百戦不殆. "
        "Keep the established Vietnamese title and resolve the alias inside inheritance-factor text."
    ),
}

TITLE_DECISION = {
    "decision_id": "audit.finding.skill-no-reason-zhixiao-baizhan-title",
    "source_zh_cn": SOURCE_ZH_COMMA,
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
        "Category-147 title punctuation variant of the same No Reason unique Skill. "
        "Lock it to the established canonical target instead of normalizing 知宵 into 'biết ta'."
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
    _upsert(reviews.setdefault("decisions", []), TITLE_DECISION, "decision_id")
    if before != json.dumps(reviews, ensure_ascii=False, sort_keys=True):
        _write(reviews_path, reviews)
        changed = True

    findings_path = repo_root / "glossary" / "canonical_findings.json"
    findings = _load(findings_path, {"schema_version": 1, "findings": []})
    before = json.dumps(findings, ensure_ascii=False, sort_keys=True)
    matched_ids: set[str] = set()
    for finding in findings.get("findings", []):
        if not isinstance(finding, dict):
            continue
        finding_id = str(finding.get("finding_id") or "")
        if finding_id not in FINDING_IDS:
            continue
        matched_ids.add(finding_id)
        suggestions = [str(value) for value in finding.get("suggested_targets_vi", []) if str(value)]
        if TARGET not in suggestions:
            suggestions.append(TARGET)
        finding["suggested_targets_vi"] = suggestions
    missing = [finding_id for finding_id in FINDING_IDS if finding_id not in matched_ids]
    if missing:
        raise ValueError(f"missing canonical findings: {', '.join(missing)}")
    if before != json.dumps(findings, ensure_ascii=False, sort_keys=True):
        _write(findings_path, findings)
        changed = True

    return changed


def main() -> int:
    changed = harden(ROOT)
    print(f"no_reason_zhixiao_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

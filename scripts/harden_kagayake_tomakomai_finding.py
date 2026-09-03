from __future__ import annotations

"""Canonicalize Hokko Tarumae's unique Skill title."""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FINDING_ID = "cf-17348d85370763d1"
SOURCE_ZH = "闪耀☆苫小牧"
SOURCE_JA = "かがやけ☆とまこまい"
TARGET = "Tỏa sáng☆Tomakomai"

RULE = {
    "id": "skill.kagayake_tomakomai",
    "category": "skill_name",
    "source_aliases": [SOURCE_ZH],
    "preferred": TARGET,
    "compact": [],
    "accepted": [TARGET],
    "forbidden": [],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "match_mode": "exact",
    "basis": (
        "The zh-CN title 闪耀☆苫小牧 is Hokko Tarumae's unique Skill whose JP "
        "player-facing title is かがやけ☆とまこまい. The existing Vietnamese "
        "Tỏa sáng☆Tomakomai preserves the imperative shine meaning and the Tomakomai "
        "place name, so lock it without introducing unnecessary translation churn."
    ),
}

DECISION = {
    "decision_id": "audit.finding.skill-kagayake-tomakomai",
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
        "JP-backed identity: 闪耀☆苫小牧 corresponds to Hokko Tarumae's unique Skill "
        "かがやけ☆とまこまい. Lock the existing Vietnamese title and scope the rule "
        "to the exact Skill title in text_data_dict.json."
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
    print(f"kagayake_tomakomai_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

"""Canonicalize the recurring in-world magazine title 月刊Twinkle."""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ZH = "月刊Twinkle"
SOURCE_JA = "月刊トゥインクル"
TARGET = "Monthly Twinkle"
KEYS = ["Champions0507", "Champions187003"]
FINDING_IDS = {"cf-3f76c45986ceefe6", "cf-fc0ace892355f4ce"}

RULE = {
    "id": "publication.monthly_twinkle",
    "category": "proper_name",
    "source_aliases": [SOURCE_ZH],
    "preferred": TARGET,
    "compact": [],
    "accepted": [TARGET],
    "forbidden": ["Đặc san Twinkle", "Twinkle - Đặc san"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["localize_dict.json"],
    "key_exact": KEYS,
    "match_mode": "contains",
    "basis": (
        "Cygames' official JP portal identifies 月刊トゥインクル as the recurring in-world magazine "
        "where Otonashi Etsuko works. The pinned zh-CN UI preserves the Latin title element as 月刊Twinkle, "
        "and established English-language Umamusume references render the publication as Monthly Twinkle. "
        "Use one proper-title rendering for the base publication name while leaving 号外/增刊 suffix wording "
        "to the containing item. Scope the contains rule only to the two known Champions keys."
    ),
}

DECISION = {
    "decision_id": "audit.finding.publication-monthly-twinkle",
    "source_zh_cn": SOURCE_ZH,
    "action": "lock",
    "target_vi": TARGET,
    "kind": "proper_name",
    "category": "proper_name",
    "ja": [SOURCE_JA],
    "en": [TARGET],
    "invalidation_scope": "item",
    "source_paths": ["localize_dict.json"],
    "key_exact": KEYS,
    "match_mode": "contains",
    "note": (
        "The two live findings are variants of the same recurring publication title. Lock only the base "
        "magazine identity as Monthly Twinkle on Champions0507 and Champions187003; edition suffixes remain "
        "ordinary item text and are not canonicalized by this rule."
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
    matched: set[str] = set()
    for finding in findings.get("findings", []):
        if not isinstance(finding, dict) or finding.get("finding_id") not in FINDING_IDS:
            continue
        matched.add(str(finding["finding_id"]))
        suggestions = [str(value) for value in finding.get("suggested_targets_vi", []) if str(value)]
        if TARGET not in suggestions:
            suggestions.append(TARGET)
        finding["suggested_targets_vi"] = suggestions
    missing = FINDING_IDS - matched
    if missing:
        raise ValueError(f"missing canonical findings: {sorted(missing)}")
    if before != json.dumps(findings, ensure_ascii=False, sort_keys=True):
        _write(findings_path, findings)
        changed = True

    return changed


def main() -> int:
    changed = harden(ROOT)
    print(f"monthly_twinkle_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

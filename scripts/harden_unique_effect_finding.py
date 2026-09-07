from __future__ import annotations

"""Canonicalize support-card 固有加成 as Global-facing Unique Effect."""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ZH = "固有加成"
SOURCE_JA = "固有ボーナス"
TARGET = "Unique Effect"
FINDING_IDS = {"cf-5cc239af1c9d7710", "cf-823a42e63df66f92"}

RULE = {
    "id": "support.unique_effect.localize",
    "category": "system_label",
    "source_aliases": [SOURCE_ZH],
    "preferred": TARGET,
    "compact": [],
    "accepted": [TARGET],
    "forbidden": ["Bonus riêng", "Unique Bonus"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["localize_dict.json"],
    "match_mode": "exact",
    "basis": (
        "The pinned zh-CN identity 固有加成 corresponds to JP 固有ボーナス, the intrinsic effect block on Support Cards. "
        "Released English support-card references use the player-facing label Unique Effect. Match only the exact source identity in localize_dict; "
        "this safely resolves both the standalone-label finding and the details-label finding whose canonical source identity is the same base label."
    ),
}

DECISION = {
    "decision_id": "audit.finding.support-unique-effect",
    "source_zh_cn": SOURCE_ZH,
    "action": "lock",
    "target_vi": TARGET,
    "kind": "system_label",
    "category": "system_label",
    "ja": [SOURCE_JA],
    "en": [TARGET],
    "invalidation_scope": "item",
    "source_paths": ["localize_dict.json"],
    "match_mode": "exact",
    "note": (
        "Canonicalize the shared Support Card 固有加成 identity as Unique Effect. Exact source-identity matching avoids consuming generic 固有/加成 prose."
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
    print(f"unique_effect_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

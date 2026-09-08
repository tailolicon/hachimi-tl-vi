from __future__ import annotations

"""Persist the verified identity for Mejiro Ramonu's unique Skill 解けぬ結い目."""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FINDING_ID = "cf-03735d8f77de39a1"
SOURCE_ZH = "至死不渝的爱"
TARGET = "解けぬ結い目"
RULE_ID = "proper_name.mejiro_ramonu_tokenu_yuime.skill110861"
DECISION_ID = "audit.finding.mejiro-ramonu-tokenu-yuime"

RULE = {
    "id": RULE_ID,
    "category": "proper_name",
    "source_aliases": [SOURCE_ZH, TARGET],
    "preferred": TARGET,
    "compact": [],
    "accepted": [TARGET],
    "forbidden": [SOURCE_ZH, "Tình yêu không đổi đến chết"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [["172"]],
    "match_mode": "contains",
    "basis": (
        "Repository evidence identifies numeric Skill 110861 as Mejiro Ramonu [Untouchable Eden]'s "
        "unique Skill 解けぬ結い目 and verifies that zh-CN 至死不渝的爱 is the corresponding title. "
        "No official Global title is available in the repository evidence, so preserve the verified JP identity."
    ),
}

DECISION = {
    "decision_id": DECISION_ID,
    "source_zh_cn": SOURCE_ZH,
    "action": "lock",
    "target_vi": TARGET,
    "kind": "proper_name",
    "category": "skill_name",
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [["172"]],
    "match_mode": "contains",
    "note": "Verified Skill 110861 identity: Mejiro Ramonu [Untouchable Eden] unique Skill 解けぬ結い目.",
}


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
    found = False
    for finding in findings.get("findings", []):
        if isinstance(finding, dict) and finding.get("finding_id") == FINDING_ID:
            found = True
            suggestions = [str(v) for v in finding.get("suggested_targets_vi", []) if str(v)]
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
    print(f"mejiro_ramonu_tokenu_yuime_changed={str(harden(ROOT)).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

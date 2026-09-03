from __future__ import annotations

"""Canonicalize Cesario's unique Skill Guiding Sea with inheritance-safe scope."""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FINDING_ID = "cf-a7a33a0b139e1f56"
SOURCE_ZH = "海纳百川"
SOURCE_JA = "Guiding Sea"
TARGET = "Guiding Sea"
RULE_ID = "skill.cesario.guiding_sea"
DECISION_ID = "audit.finding.skill-cesario-guiding-sea"
PATH_PREFIXES = [["172"]]

RULE = {
    "id": RULE_ID,
    "category": "skill_name",
    "source_aliases": [SOURCE_ZH],
    "preferred": TARGET,
    "compact": [],
    "accepted": [TARGET],
    "forbidden": ["Biển dung trăm sông", "Biển ôm trọn trăm sông"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": PATH_PREFIXES,
    "match_mode": "contains",
    "basis": (
        "Game ID 1110 is Cesario / シーザリオ. Current JP gameplay references identify her unique "
        "Skill as the English title Guiding Sea. The zh-CN bridge 海纳百川 occurs inside category-172 "
        "Spark/inheritance text for Skill IDs 11100101-11100103. Preserve Guiding Sea there rather than "
        "promoting a semantic zh-CN calque. Category scoping prevents the Chinese idiom 海纳百川 from "
        "being rewritten if it appears as ordinary prose elsewhere."
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
    "json_path_prefixes": PATH_PREFIXES,
    "match_mode": "contains",
    "note": (
        "JP-backed Cesario unique-Skill identity is Guiding Sea. Lock the complete zh-CN Skill alias "
        "inside category-172 inheritance/Spark text only; do not generalize the Chinese idiom to prose."
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
        # All live evidence for this finding is category-172 Skill Spark/inheritance text.
        # Correct the over-broad historical finding scope before resolving it.
        finding["json_path_prefixes"] = PATH_PREFIXES
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
    print(f"cesario_guiding_sea_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

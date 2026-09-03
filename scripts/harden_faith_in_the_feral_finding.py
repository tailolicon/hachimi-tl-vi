from __future__ import annotations

"""Canonicalize Jungle Pocket's unique Skill Faith in the Feral."""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FINDING_IDS = ("cf-218ec5e342978091", "cf-ee7eb4b1cd8aca0a")
SOURCE_ZH = "狂野信仰"
SOURCE_JA = "Faith in the Feral"
TARGET = "Faith in the Feral"
HISTORICAL_TARGET = "Tín ngưỡng hoang dã"

RULE = {
    "id": "skill.jungle_pocket.faith_in_the_feral",
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
        "Jungle Pocket's current JP unique Skill title is literally the English title "
        "'Faith in the Feral'. zh-CN 狂野信仰 is a localized bridge title, and the historical "
        "Vietnamese 'Tín ngưỡng hoang dã' translates that bridge instead of preserving the "
        "in-game Skill identity. Keep 'Faith in the Feral' verbatim. The exact source alias "
        "plus text_data_dict.json scope covers the duplicate live finding scopes without "
        "matching longer prose that only contains the title."
    ),
}

DECISION = {
    "decision_id": "audit.finding.skill-faith-in-the-feral",
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
        "JP-backed identity for Jungle Pocket's unique Skill is the verbatim title "
        "'Faith in the Feral'. Lock the in-game title and reject the zh-CN-order/localized "
        "Vietnamese calque 'Tín ngưỡng hoang dã'."
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
    print(f"faith_in_the_feral_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

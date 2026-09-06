from __future__ import annotations

"""Canonicalize the JP-only 大豊食祭 scenario short title by stable JP identity."""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "大丰食祭"
TARGET = "Daihoushokusai"
FINDING_ID = "cf-5310cb8fbcc8798f"

RULE = {
    "id": "scenario.daihoushokusai.short",
    "category": "scenario",
    "source_aliases": [SOURCE],
    "preferred": TARGET,
    "compact": [],
    "accepted": [TARGET],
    "forbidden": ["Đại Lễ hội Ẩm thực", "Đại lễ hội ẩm thực"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["localize_dict.json"],
    "key_prefixes": ["SingleModeScenarioCook"],
    "match_mode": "contains",
    "basis": (
        "JP-only training scenario identity. Official JP material names the scenario "
        "収穫ッ！満腹ッ！大豊食祭 and commonly abbreviates it to 大豊食祭. No official Global "
        "localization is available for this scenario yet, so preserve the stable romanized short "
        "identity Daihoushokusai rather than presenting a Vietnamese semantic calque as canonical."
    ),
}

DECISION = {
    "decision_id": "audit.finding.scenario-daihoushokusai-short",
    "source_zh_cn": SOURCE,
    "action": "lock",
    "target_vi": TARGET,
    "kind": "scenario_name",
    "category": "scenario",
    "invalidation_scope": "item",
    "source_paths": ["localize_dict.json"],
    "key_prefixes": ["SingleModeScenarioCook"],
    "match_mode": "contains",
    "note": (
        "Official JP identity is 収穫ッ！満腹ッ！大豊食祭, with 大豊食祭 used as the short scenario "
        "name. Until an official Global title exists, use the romanized short identity "
        "Daihoushokusai in the scoped cooking-scenario UI instead of a semantic calque."
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
        if not isinstance(finding, dict) or str(finding.get("finding_id") or "") != FINDING_ID:
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
    print(f"gourmet_festival_scenario_hardening_changed={str(harden(ROOT)).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

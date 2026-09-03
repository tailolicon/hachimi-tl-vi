from __future__ import annotations

"""Prevent generic zh-CN grass prose from overmatching the Turf race surface."""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FINDING_ID = "cf-b5b4efe029e4fb75"
SOURCE_ZH = "草地"
TARGET = "Turf"
BASE_RULE_ID = "common.surface.turf"
ZH_RULE_ID = "common.surface.turf.zhcn"
APTITUDE_RULE_ID = "common.surface.turf.aptitude"

ZH_RULE = {
    "id": ZH_RULE_ID,
    "category": "race_surface",
    "source_aliases": [SOURCE_ZH],
    "preferred": TARGET,
    "compact": [],
    "accepted": [TARGET],
    "forbidden": ["Sân cỏ"],
    "require_accepted": True,
    "basis": (
        "zh-CN 草地 is the player-facing Turf surface label when it is itself the "
        "label. Exact matching prevents ordinary narrative grass/grassland prose "
        "from being normalized to the racing-surface term."
    ),
    "match_mode": "exact",
}

APTITUDE_RULE = {
    "id": APTITUDE_RULE_ID,
    "category": "race_surface",
    "source_aliases": [SOURCE_ZH],
    "preferred": TARGET,
    "compact": [],
    "accepted": [TARGET],
    "forbidden": ["Sân cỏ"],
    "require_accepted": True,
    "basis": (
        "SingleMode0078 is the scoped zh-CN Turf Aptitude UI label 草地适性. "
        "Keep the Turf component available there without restoring a global "
        "substring matcher for narrative 草地 prose."
    ),
    "source_paths": ["localize_dict.json"],
    "key_exact": ["SingleMode0078"],
    "match_mode": "contains",
}

DECISION = {
    "decision_id": "audit.finding.turf-surface-zhcn-context",
    "source_zh_cn": SOURCE_ZH,
    "action": "lock",
    "target_vi": TARGET,
    "kind": "context_rule",
    "category": "race_surface",
    "match_mode": "exact",
    "note": (
        "Lock standalone 草地 to Turf while rejecting substring matches in ordinary "
        "grass/grassland prose. The JP 芝 alias remains on the established base rule, "
        "and SingleMode0078 gets a separate scoped composition rule for 草地适性."
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
    terms = community.setdefault("terms", [])
    base_found = False
    for term in terms:
        if not isinstance(term, dict) or term.get("id") != BASE_RULE_ID:
            continue
        base_found = True
        aliases = [str(alias) for alias in term.get("source_aliases", []) if str(alias)]
        term["source_aliases"] = [alias for alias in aliases if alias != SOURCE_ZH]
        basis = str(term.get("basis") or "")
        if "zh-CN 草地" not in basis:
            term["basis"] = (
                basis.rstrip() + " zh-CN 草地 is handled by scoped sibling rules "
                "so narrative grass prose cannot overmatch."
            ).strip()
        break
    if not base_found:
        raise ValueError(f"missing community term {BASE_RULE_ID}")
    _upsert(terms, ZH_RULE, "id")
    _upsert(terms, APTITUDE_RULE, "id")
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
    print(f"turf_surface_context_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

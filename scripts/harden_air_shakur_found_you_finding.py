from __future__ import annotations

"""Canonicalize Air Shakur unique Skill: JP …found you. / zh-CN ...抓到你了。"""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FINDING_ID = "cf-2c4b6d109aaf229d"
SOURCE_ZH = "...抓到你了。"
SOURCE_JA = "…found you."
TARGET = "…found you."
HISTORICAL_TARGET = "...Bắt được bạn rồi."
PATH_PREFIX = ["172"]

RULE = {
    "id": "skill.air_shakur_found_you",
    "category": "skill_name",
    "source_aliases": [SOURCE_ZH],
    "preferred": TARGET,
    "compact": [],
    "accepted": [TARGET],
    "forbidden": [HISTORICAL_TARGET],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [PATH_PREFIX],
    "match_mode": "contains",
    "basis": (
        "Air Shakur trainee 103602 ([Belphegor's Prime]) owns unique Skill 110361 whose Japanese-game "
        "title is itself the English text '…found you.'. The zh-CN bridge translates that title as "
        "'...抓到你了。'. Preserve the JP title verbatim instead of retaining the historical Vietnamese "
        "semantic calque. Scope the alias to inheritance descriptions under text_data_dict category 172."
    ),
}

DECISION = {
    "decision_id": "audit.finding.skill-air-shakur-found-you",
    "source_zh_cn": SOURCE_ZH,
    "action": "lock",
    "target_vi": TARGET,
    "kind": "skill_name",
    "category": "skill_name",
    "ja": [SOURCE_JA],
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [PATH_PREFIX],
    "match_mode": "contains",
    "note": (
        "Verified unique Skill 110361 for [Belphegor's Prime] Air Shakur. Its JP title is already "
        "'…found you.', so preserve that exact title and reject the historical Vietnamese calque."
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
        if isinstance(finding, dict) and finding.get("finding_id") == FINDING_ID:
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
    print(f"air_shakur_found_you_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

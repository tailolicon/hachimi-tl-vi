from __future__ import annotations

"""Canonicalize Sounds of Earth's unique Skill Vivace Volare."""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FINDING_IDS = ("cf-5b78375546baf889", "cf-d43d81c9ed4244b6")
SOURCE_ZH = "活泼乐章・飞驰"
SOURCE_JA = "ヴィヴァーチェ・ヴォラーレ"
TARGET = "Vivace Volare"
HISTORICAL_TARGETS = [
    "Khúc nhạc rộn ràng・Phi nước đại",
    "Khúc nhạc sôi nổi・Phi nhanh",
]

RULE = {
    "id": "skill.sounds_of_earth.vivace_volare",
    "category": "skill_name",
    "source_aliases": [SOURCE_ZH],
    "preferred": TARGET,
    "compact": [],
    "accepted": [TARGET],
    "forbidden": HISTORICAL_TARGETS,
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "match_mode": "contains",
    "basis": (
        "Sounds of Earth's unique Skill is JP ヴィヴァーチェ・ヴォラーレ, Skill 101021. "
        "Current English-language reference material renders the Italian title as 'Vivace Volare'. "
        "Preserve that proper-name identity instead of translating the localized zh-CN bridge "
        "活泼乐章・飞驰 into competing Vietnamese calques. Contains matching is intentional because "
        "the same title is embedded verbatim in category-172 inheritance-factor descriptions."
    ),
}

DECISION = {
    "decision_id": "audit.finding.skill-sounds-of-earth-vivace-volare",
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
        "JP-backed identity: Sounds of Earth's unique Skill is ヴィヴァーチェ・ヴォラーレ "
        "(Skill 101021). Preserve the Latin rendering 'Vivace Volare' across the title and "
        "inheritance-factor references rather than keeping zh-CN-derived Vietnamese calques."
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
    print(f"sounds_of_earth_vivace_volare_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

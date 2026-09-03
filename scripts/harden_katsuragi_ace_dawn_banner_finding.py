from __future__ import annotations

"""Canonicalize Katsuragi Ace's unique Skill 拂晓御旗『葛城荣主』！ / JP 暁の御旗『葛城栄主』！."""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FINDING_ID = "cf-abda2b1124d162ff"
SOURCE_ZH = "拂晓御旗『葛城荣主』！"
SOURCE_JA = "暁の御旗『葛城栄主』！"
TARGET = "Ngự Kỳ Bình Minh 『Katsuragi Ace』!"
RULE_ID = "skill.katsuragi_ace.akatsuki_no_mihata"
DECISION_ID = "audit.finding.skill-katsuragi-ace-akatsuki-no-mihata"

RULE = {
    "id": RULE_ID,
    "category": "skill_name",
    "source_aliases": [SOURCE_ZH],
    "preferred": TARGET,
    "compact": [],
    "accepted": [TARGET],
    "forbidden": ["Ngự kỳ bình minh 『Katsuragi Ace』!"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "match_mode": "contains",
    "basis": (
        "Repository locator 47:101041 is verified as JP 暁の御旗『葛城栄主』！, Katsuragi Ace's "
        "unique Skill. The quoted 葛城栄主 is stylized kanji wordplay for Katsuragi Ace, so "
        "preserve the canonical Roman character name rather than calquing zh-CN 葛城荣主. "
        "The established Vietnamese rendering 'Ngự kỳ bình minh' is faithful to 暁の御旗; "
        "normalize game-title capitalization to 'Ngự Kỳ Bình Minh'. Contains matching is "
        "needed because the complete Skill title appears inside category-172 inheritance descriptions."
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
    "match_mode": "contains",
    "note": (
        "JP-backed identity for locator 47:101041: 暁の御旗『葛城栄主』！. Preserve "
        "Katsuragi Ace in Roman letters and normalize the established Vietnamese title to "
        "'Ngự Kỳ Bình Minh 『Katsuragi Ace』!'."
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
    print(f"katsuragi_ace_dawn_banner_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

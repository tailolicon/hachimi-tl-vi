from __future__ import annotations

"""Prevent generic Mood aliases from matching the distinct 干劲十足 Skill title."""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
COMMUNITY_TERM_ID = "common.state.mood"
BRIDGE_TERM_ID = "state.mood"
SKILL_TERM_ID = "skill.ikigomi_jubun"
SOURCE_ZH = "干劲十足"
PREFERRED = "Khí thế tràn đầy"

SKILL_TERM = {
    "id": SKILL_TERM_ID,
    "category": "skill_name",
    "source_aliases": [SOURCE_ZH],
    "preferred": PREFERRED,
    "accepted": [PREFERRED],
    "forbidden": ["Tràn đầy khí thế", "Mood"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [["147"]],
    "match_mode": "exact",
    "basis": "Locator 202312 in the maintained curation evidence verifies JP 意気込み十分 for zh-CN 干劲十足. This is a Skill title, not the generic やる気 / 干劲 Mood state; use the reviewed Vietnamese title Khí thế tràn đầy.",
}

SKILL_DECISION = {
    "decision_id": "audit.finding.skill-ikigomi-jubun",
    "source_zh_cn": SOURCE_ZH,
    "action": "lock",
    "target_vi": PREFERRED,
    "kind": "skill_name",
    "category": "skill_name",
    "ja": ["意気込み十分"],
    "note": "Verified curation locator 202312 identifies JP 意気込み十分; keep this Skill identity separate from the generic Mood state.",
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


def _upsert(items: list[Any], record: dict[str, Any], *, id_field: str) -> None:
    record_id = str(record[id_field])
    for index, item in enumerate(items):
        if isinstance(item, dict) and str(item.get(id_field) or "") == record_id:
            merged = dict(item)
            merged.update(record)
            items[index] = merged
            return
    items.append(dict(record))


def _add_exclusion(path: Path, term_id: str, basis: str) -> bool:
    payload = _load(path)
    terms = payload.get("terms", [])
    if not isinstance(terms, list):
        raise ValueError(f"{path} terms must be a list")

    before = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    matched = False
    for term in terms:
        if not isinstance(term, dict) or str(term.get("id") or "") != term_id:
            continue
        matched = True
        exclusions = [str(value) for value in term.get("exclude_source_contains", []) if str(value)]
        term["exclude_source_contains"] = list(dict.fromkeys([*exclusions, SOURCE_ZH]))
        term["basis"] = basis
        break
    if not matched:
        raise ValueError(f"missing canonical term {term_id} in {path}")

    changed = before != json.dumps(payload, ensure_ascii=False, sort_keys=True)
    if changed:
        _write(path, payload)
    return changed


def harden(repo_root: Path = ROOT) -> bool:
    community_path = repo_root / "glossary" / "ui_community_terms.json"
    community_changed = _add_exclusion(
        community_path,
        COMMUNITY_TERM_ID,
        "Mood is the generic player-facing やる気 / 干劲 state. The exact zh-CN Skill title 干劲十足 (JP 意気込み十分) is a distinct Skill identity and must not inherit the generic Mood matcher by substring.",
    )
    community = _load(community_path, {"schema_version": 1, "terms": []})
    terms = community.setdefault("terms", [])
    if not isinstance(terms, list):
        raise ValueError("glossary/ui_community_terms.json terms must be a list")
    before = json.dumps(community, ensure_ascii=False, sort_keys=True)
    _upsert(terms, SKILL_TERM, id_field="id")
    if before != json.dumps(community, ensure_ascii=False, sort_keys=True):
        _write(community_path, community)
        community_changed = True

    bridge_changed = _add_exclusion(
        repo_root / "glossary" / "source_bridge_terms.json",
        BRIDGE_TERM_ID,
        "干劲 is the zh-CN bridge for the generic Mood state, but the exact Skill title 干劲十足 corresponds to JP 意気込み十分 and must not be normalized to Mood by substring matching.",
    )

    reviews_path = repo_root / "glossary" / "terminology_reviews.json"
    reviews = _load(reviews_path, {"schema_version": 1, "decisions": []})
    decisions = reviews.setdefault("decisions", [])
    if not isinstance(decisions, list):
        raise ValueError("glossary/terminology_reviews.json decisions must be a list")
    before = json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    _upsert(decisions, SKILL_DECISION, id_field="decision_id")
    reviews_changed = before != json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    if reviews_changed:
        _write(reviews_path, reviews)

    return community_changed or bridge_changed or reviews_changed


def main() -> int:
    changed = harden(ROOT)
    print(f"mood_skill_title_context_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

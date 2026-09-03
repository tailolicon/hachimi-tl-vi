from __future__ import annotations

"""Canonicalize Skill 202712, 会心の一歩 / 会心一步.

The existing Vietnamese `Bước quyết tâm` confuses 会心 with determination.
Japanese 会心 means a result or move that goes as intended and gives
satisfaction; keep that semantic distinction in the compact Skill title.
"""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FINDING_ID = "cf-07a7131770d2b792"
SOURCE_ZH = "会心一步"
SOURCE_JA = "会心の一歩"
PREFERRED = "Bước Chân Đắc Ý"

KAISHIN_STEP = {
    "id": "skill.kaishin_step",
    "category": "skill_name",
    "source_aliases": [SOURCE_ZH],
    "preferred": PREFERRED,
    "compact": [],
    "accepted": [PREFERRED],
    "forbidden": ["Bước quyết tâm"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "match_mode": "exact",
    "basis": (
        "Pinned Skill 202712 is JP 会心の一歩. Japanese 会心 denotes something "
        "going exactly as intended / to one's satisfaction, not resolve or "
        "determination. Use Bước Chân Đắc Ý to preserve that distinction in a "
        "compact Vietnamese Skill title, and reject the old Bước quyết tâm rendering."
    ),
}

KAISHIN_STEP_DECISION = {
    "decision_id": "audit.finding.skill-kaishin-step",
    "source_zh_cn": SOURCE_ZH,
    "action": "lock",
    "target_vi": PREFERRED,
    "kind": "skill_name",
    "category": "skill_name",
    "ja": [SOURCE_JA],
    "note": (
        "Repository curation verifies Skill 202712 / JP 会心の一歩. Dictionary "
        "semantics for 会心 are 'to one's satisfaction / as intended'; therefore "
        "Bước Chân Đắc Ý is the stable JP-guarded title and Bước quyết tâm is a "
        "meaning-changing mistranslation."
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


def _upsert(items: list[Any], record: dict[str, Any], *, id_field: str) -> None:
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
    terms = community.setdefault("terms", [])
    if not isinstance(terms, list):
        raise ValueError("glossary/ui_community_terms.json terms must be a list")
    before = json.dumps(community, ensure_ascii=False, sort_keys=True)
    _upsert(terms, KAISHIN_STEP, id_field="id")
    if before != json.dumps(community, ensure_ascii=False, sort_keys=True):
        _write(community_path, community)
        changed = True

    reviews_path = repo_root / "glossary" / "terminology_reviews.json"
    reviews = _load(reviews_path, {"schema_version": 1, "decisions": []})
    decisions = reviews.setdefault("decisions", [])
    if not isinstance(decisions, list):
        raise ValueError("glossary/terminology_reviews.json decisions must be a list")
    before = json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    _upsert(decisions, KAISHIN_STEP_DECISION, id_field="decision_id")
    if before != json.dumps(reviews, ensure_ascii=False, sort_keys=True):
        _write(reviews_path, reviews)
        changed = True

    return changed


def main() -> int:
    changed = harden(ROOT)
    print(f"kaishin_step_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

"""Canonicalize Manhattan Cafe's unique Skill 逐君之形 / アナタヲ・オイカケテ.

The older curation pass correctly deferred the zh-CN semantic bridge because the
stylized JP title did not yet have a stable project-facing localization. The
English release now provides the source-backed title "Chasing After You" for the
same Manhattan Cafe [Creeping Shadow] unique Skill. Preserve that official
English localization instead of translating backward from the zh-CN wording.
"""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FINDING_ID = "cf-04c407aa449b0c6e"
PREFERRED = "Chasing After You"

CHASING_AFTER_YOU = {
    "id": "skill.manhattan_cafe.chasing_after_you",
    "category": "skill_name",
    "source_aliases": ["逐君之形"],
    "preferred": PREFERRED,
    "compact": [],
    "accepted": [PREFERRED],
    "forbidden": ["Hình bóng đuổi theo người"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [["147"]],
    "match_mode": "exact",
    "basis": (
        "Skill ID 100251 is JP アナタヲ・オイカケテ for Manhattan Cafe [Creeping Shadow]. "
        "The English release localizes that exact unique Skill as Chasing After You. "
        "Use the stable English localization rather than preserving the semantic zh-CN bridge "
        "逐君之形 or its older Vietnamese back-translation."
    ),
}

CHASING_AFTER_YOU_DECISION = {
    "decision_id": "audit.finding.skill-manhattan-cafe-chasing-after-you",
    "source_zh_cn": "逐君之形",
    "action": "lock",
    "target_vi": PREFERRED,
    "kind": "skill_name",
    "category": "skill_name",
    "ja": ["アナタヲ・オイカケテ"],
    "note": (
        "Repository curation maps 逐君之形 to Skill ID 100251 / JP アナタヲ・オイカケテ; "
        "the English release now supplies the stable title Chasing After You, so the prior "
        "stylization defer can be resolved without inventing a Vietnamese proper title."
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
    _upsert(terms, CHASING_AFTER_YOU, id_field="id")
    if before != json.dumps(community, ensure_ascii=False, sort_keys=True):
        _write(community_path, community)
        changed = True

    reviews_path = repo_root / "glossary" / "terminology_reviews.json"
    reviews = _load(reviews_path, {"schema_version": 1, "decisions": []})
    decisions = reviews.setdefault("decisions", [])
    if not isinstance(decisions, list):
        raise ValueError("glossary/terminology_reviews.json decisions must be a list")
    before = json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    _upsert(decisions, CHASING_AFTER_YOU_DECISION, id_field="decision_id")
    if before != json.dumps(reviews, ensure_ascii=False, sort_keys=True):
        _write(reviews_path, reviews)
        changed = True

    return changed


def main() -> int:
    changed = harden(ROOT)
    print(f"manhattan_cafe_chasing_after_you_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

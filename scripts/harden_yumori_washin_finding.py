from __future__ import annotations

"""Canonicalize Wonder Acute's JP-only unique Skill 湯守の和心."""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FINDING_ID = "cf-141e1dbe5b4bc506"
SOURCE_ZH = "汤守的和心"
SOURCE_JA = "湯守の和心"
PREFERRED = "Tấm Lòng Người Giữ Suối Nóng"
TERM_ID = "skill.wonder_acute.yumori_washin"

TERM = {
    "id": TERM_ID,
    "category": "skill_name",
    "source_aliases": [SOURCE_ZH],
    "preferred": PREFERRED,
    "compact": [],
    "accepted": [PREFERRED],
    "forbidden": ["Tấm lòng hòa ái của người trông suối nước nóng"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "match_mode": "contains",
    "basis": (
        "Repository factor keys map zh-CN 汤守的和心 to Wonder Acute's JP-only unique Skill 湯守の和心. "
        "Current JP game references independently identify the exact title, owner, and effect. Following the repository's "
        "JP-only Skill policy, preserve the Japanese semantic identity in a compact Vietnamese game title: 湯守 is the "
        "keeper/caretaker of the hot spring and 和心 is the harmonious/gentle heart."
    ),
}

DECISION = {
    "decision_id": "audit.finding.skill-wonder-acute-yumori-washin",
    "source_zh_cn": SOURCE_ZH,
    "action": "lock",
    "target_vi": PREFERRED,
    "kind": "skill_name",
    "category": "skill_name",
    "ja": [SOURCE_JA],
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "match_mode": "contains",
    "note": (
        "Verified JP identity is Wonder Acute's unique Skill 湯守の和心. Use the compact Vietnamese title "
        "Tấm Lòng Người Giữ Suối Nóng rather than the existing sentence-like gloss."
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
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


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
    _upsert(terms, TERM, id_field="id")
    if before != json.dumps(community, ensure_ascii=False, sort_keys=True):
        _write(community_path, community)
        changed = True

    reviews_path = repo_root / "glossary" / "terminology_reviews.json"
    reviews = _load(reviews_path, {"schema_version": 1, "decisions": []})
    decisions = reviews.setdefault("decisions", [])
    if not isinstance(decisions, list):
        raise ValueError("glossary/terminology_reviews.json decisions must be a list")
    before = json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    _upsert(decisions, DECISION, id_field="decision_id")
    if before != json.dumps(reviews, ensure_ascii=False, sort_keys=True):
        _write(reviews_path, reviews)
        changed = True
    return changed


def main() -> int:
    changed = harden(ROOT)
    print(f"yumori_washin_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

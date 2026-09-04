from __future__ import annotations

"""Canonicalize Gentildonna's unique Skill 不凋なるCattleya from zh-CN 永不凋零的Cattleya."""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ZH = "永不凋零的Cattleya"
SOURCE_JA = "不凋なるCattleya"
PREFERRED = "Cattleya Bất Tàn"
TERM_ID = "skill.gentildonna.unfading_cattleya"

TERM = {
    "id": TERM_ID,
    "category": "skill_name",
    "source_aliases": [SOURCE_ZH],
    "preferred": PREFERRED,
    "compact": [],
    "accepted": [PREFERRED],
    "forbidden": ["Cattleya không bao giờ tàn"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "match_mode": "contains",
    "basis": (
        "Repository factor IDs 11160201-11160203 belong to [La dama perfetta] Gentildonna. Current JP character data "
        "identifies that outfit's unique Skill exactly as 不凋なるCattleya. The zh-CN title preserves the same meaning, "
        "but the existing Vietnamese sentence-like gloss is too long for a proper Skill title. Use the compact title "
        "Cattleya Bất Tàn while preserving the Latin flower name from the JP original."
    ),
}

DECISION = {
    "decision_id": "audit.finding.skill-gentildonna-unfading-cattleya",
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
        "Verified JP identity is [La dama perfetta] Gentildonna's unique Skill 不凋なるCattleya. "
        "Preserve Cattleya and render 不凋なる as the compact Vietnamese title Cattleya Bất Tàn."
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
    rid = str(record[id_field])
    for index, item in enumerate(items):
        if isinstance(item, dict) and str(item.get(id_field) or "") == rid:
            merged = dict(item)
            merged.update(record)
            items[index] = merged
            return
    items.append(dict(record))


def harden(repo_root: Path = ROOT) -> bool:
    changed = False
    for filename, collection, record, id_field in [
        ("ui_community_terms.json", "terms", TERM, "id"),
        ("terminology_reviews.json", "decisions", DECISION, "decision_id"),
    ]:
        path = repo_root / "glossary" / filename
        payload = _load(path, {"schema_version": 1, collection: []})
        items = payload.setdefault(collection, [])
        if not isinstance(items, list):
            raise ValueError(f"{path} {collection} must be a list")
        before = json.dumps(payload, ensure_ascii=False, sort_keys=True)
        _upsert(items, record, id_field=id_field)
        if before != json.dumps(payload, ensure_ascii=False, sort_keys=True):
            _write(path, payload)
            changed = True
    return changed


def main() -> int:
    changed = harden(ROOT)
    print(f"unfading_cattleya_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

"""Canonicalize Fine Motion's skill 麗走一直！ラーメン道 from the zh-CN bridge title."""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ZH = "丽影飞驰！拉面道"
SOURCE_JA = "麗走一直！ラーメン道"
PREFERRED = "Lệ Ảnh Phi Trì! Đạo Ramen"
HISTORICAL = "Bóng đẹp phi nhanh! Đạo Ramen"
TERM_ID = "skill.fine_motion.reisou_ichoku_ramen_do"
PATH_PREFIX = ["147"]

TERM = {
    "id": TERM_ID,
    "category": "skill_name",
    "source_aliases": [SOURCE_ZH],
    "preferred": PREFERRED,
    "compact": [],
    "accepted": [PREFERRED],
    "forbidden": [HISTORICAL],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [PATH_PREFIX],
    "match_mode": "exact",
    "basis": (
        "Verified Fine Motion skill title is JP 麗走一直！ラーメン道. The zh-CN bridge title 丽影飞驰！拉面道 "
        "compresses the same graceful-running + ramen-path motif. Follow skill_name_style by preserving that compact "
        "title rhythm as 'Lệ Ảnh Phi Trì! Đạo Ramen' rather than the historical prose-like calque."
    ),
}

DECISION = {
    "decision_id": "audit.finding.fine-motion-reisou-ichoku-ramen-do",
    "source_zh_cn": SOURCE_ZH,
    "action": "lock",
    "target_vi": PREFERRED,
    "kind": "skill_name",
    "category": "skill_name",
    "ja": [SOURCE_JA],
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [PATH_PREFIX],
    "match_mode": "exact",
    "note": (
        "JP verification identifies Fine Motion's Skill as 麗走一直！ラーメン道; use the compact Vietnamese title "
        "Lệ Ảnh Phi Trì! Đạo Ramen and reject the older prose-like bridge calque."
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
    _upsert(community.setdefault("terms", []), TERM, "id")
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

    return changed


def main() -> int:
    changed = harden(ROOT)
    print(f"reisou_ichoku_ramen_do_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ALIAS = "固有加成"
TARGET = "Unique Effect"
TERM_ID = "common.character.unique_bonus"
DECISION_ID = "audit.finding.character-unique-bonus"

TERM = {
    "id": TERM_ID,
    "category": "system_label",
    "source_aliases": [ALIAS],
    "preferred": TARGET,
    "compact": [TARGET],
    "accepted": [TARGET],
    "forbidden": ["Bonus riêng", "bonus riêng", "Hiệu ứng riêng", "Unique Bonus"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["localize_dict.json"],
    "key_exact": ["Character0050", "Character0196"],
    "match_mode": "contains",
    "basis": (
        "Fresh identity verification maps the JP generic support-card section 固有ボーナス to the "
        "verified Global-facing label Unique Effect. Repository canonical policy prefers that released "
        "player-facing terminology over a locally invented Vietnamese synonym. Scope the reusable zh-CN "
        "alias 固有加成 to the two known localize UI keys so category-150 proper/display names and unrelated "
        "generic 固有 wording elsewhere are untouched."
    ),
}

REVIEW = {
    "decision_id": DECISION_ID,
    "source_zh_cn": ALIAS,
    "action": "lock",
    "target_vi": TARGET,
    "kind": "system_label",
    "category": "system_label",
    "note": (
        "Legacy decision aligned with the verified Global-facing Support-card label Unique Effect. "
        "Keep it consistent with audit.finding.support-unique-effect-label so pre-apply review-lock restoration "
        "cannot recreate the superseded Hiệu ứng riêng mapping."
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


def _upsert(rows: list[Any], key: str, value: str, payload: dict[str, Any]) -> None:
    for index, item in enumerate(rows):
        if isinstance(item, dict) and item.get(key) == value:
            merged = dict(item)
            merged.update(payload)
            rows[index] = merged
            return
    rows.append(dict(payload))


def harden(repo_root: Path = ROOT) -> bool:
    changed = False
    community_path = repo_root / "glossary" / "ui_community_terms.json"
    community = _load(community_path)
    terms = community.get("terms")
    if not isinstance(terms, list):
        raise ValueError("glossary/ui_community_terms.json terms must be a list")
    before = json.dumps(community, ensure_ascii=False, sort_keys=True)
    _upsert(terms, "id", TERM_ID, TERM)
    if before != json.dumps(community, ensure_ascii=False, sort_keys=True):
        _write(community_path, community)
        changed = True

    reviews_path = repo_root / "glossary" / "terminology_reviews.json"
    reviews = _load(reviews_path, {"schema_version": 1, "decisions": []})
    decisions = reviews.setdefault("decisions", [])
    if not isinstance(decisions, list):
        raise ValueError("glossary/terminology_reviews.json decisions must be a list")
    before = json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    _upsert(decisions, "decision_id", DECISION_ID, REVIEW)
    if before != json.dumps(reviews, ensure_ascii=False, sort_keys=True):
        _write(reviews_path, reviews)
        changed = True
    return changed


def main() -> int:
    changed = harden(ROOT)
    print(f"unique_bonus_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

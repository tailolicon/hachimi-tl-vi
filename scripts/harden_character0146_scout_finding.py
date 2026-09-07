from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TERM_ID = "common.scout.character0146"
DECISION_ID = "audit.finding.character0146-scout"
ALIAS = "奖池"
TARGET = "Chiêu mộ"

TERM = {
    "id": TERM_ID,
    "category": "system_label",
    "source_aliases": [ALIAS],
    "preferred": TARGET,
    "compact": [TARGET],
    "accepted": [TARGET],
    "forbidden": ["Kho quà"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["localize_dict.json"],
    "key_exact": ["Character0146"],
    "match_mode": "exact",
    "basis": "Cross-locale identity maps Character0146 to Scout. The zh-CN surface 奖池 is lossy here, so this bridge is exact-key scoped and must not affect ordinary prize/gacha pool uses elsewhere.",
}

REVIEW = {
    "decision_id": DECISION_ID,
    "source_zh_cn": ALIAS,
    "action": "lock",
    "target_vi": TARGET,
    "kind": "source_bridge",
    "category": "system_label",
    "note": "Character0146 is the Scout/recruitment label. Lock Chiêu mộ only through the exact-key canonical rule; generic 奖池 remains context-dependent elsewhere.",
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
    print(f"character0146_scout_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

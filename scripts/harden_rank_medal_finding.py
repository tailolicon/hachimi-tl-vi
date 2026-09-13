from __future__ import annotations

"""Resolve the one-off 等级奖牌 finding without inventing a reusable identity."""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OLD_DECISION_ID = "audit.finding.rank-medal-defer"

RANK_MEDAL_IGNORE = {
    "decision_id": "audit.finding.rank-medal-unverified-identity-ignore",
    "source_zh_cn": "等级奖牌",
    "action": "ignore",
    "target_vi": "",
    "kind": "system_label",
    "category": "system",
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [["133", "3"]],
    "match_mode": "exact",
    "note": (
        "This is the one-off player-facing label at text_data_dict.json 133/3. Repository evidence "
        "and targeted JP/Global reference checks do not establish its underlying official identity, "
        "so do not promote the current Vietnamese text or a guessed English/Japanese name into "
        "reusable canonical terminology. Resolve only the systemic canonical blocker for this exact "
        "item and leave its wording to ordinary translation review. In particular, do not conflate "
        "it with the distinct verified Trainer Medal / トレーナーメダル concept."
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
    reviews_path = repo_root / "glossary" / "terminology_reviews.json"
    reviews = _load(reviews_path, {"schema_version": 1, "decisions": []})
    decisions = reviews.setdefault("decisions", [])
    if not isinstance(decisions, list):
        raise ValueError("glossary/terminology_reviews.json decisions must be a list")

    before = json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    decisions[:] = [
        item
        for item in decisions
        if not (isinstance(item, dict) and str(item.get("decision_id") or "") == OLD_DECISION_ID)
    ]
    _upsert(decisions, RANK_MEDAL_IGNORE, id_field="decision_id")
    if before == json.dumps(reviews, ensure_ascii=False, sort_keys=True):
        return False
    _write(reviews_path, reviews)
    return True


def main() -> int:
    changed = harden(ROOT)
    print(f"rank_medal_ignore_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

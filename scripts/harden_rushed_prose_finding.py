from __future__ import annotations

"""Exclude one exact prose sentence from the reusable Rushed/焦躁 context matcher."""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FINDING_ID = "cf-78fd1f6eb5a24b5a"
SOURCE = "每当独自奔跑时，就会感受到有如针刺的疼痛，以及焦躁……\n即使如此也不停下脚步，就算可能性低于零也是。"
DECISION_ID = "audit.finding.rushed-prose-overmatch-128-1105"

DECISION = {
    "decision_id": DECISION_ID,
    "source_zh_cn": SOURCE,
    "action": "ignore",
    "kind": "context_rule",
    "category": "context_rule",
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [["128", "1105"]],
    "match_mode": "exact",
    "note": (
        "In this exact profile/prose item, 焦躁 is ordinary narrative language (restlessness/agitation), "
        "not the named race-state/system label Rushed. Keep the reusable 焦躁 -> Rushed rule intact "
        "elsewhere, but stop this single sentence from remaining a canonical blocker."
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


def _upsert_unique(items: list[Any], record: dict[str, Any], id_field: str) -> None:
    """Upsert one record and collapse same-ID duplicates left by concurrent rebases."""
    record_id = str(record[id_field])
    first_index: int | None = None
    duplicates: list[int] = []
    for index, item in enumerate(items):
        if not isinstance(item, dict) or str(item.get(id_field) or "") != record_id:
            continue
        if first_index is None:
            first_index = index
        else:
            duplicates.append(index)

    if first_index is None:
        items.append(dict(record))
        return

    merged = dict(items[first_index])
    merged.update(record)
    items[first_index] = merged
    for index in reversed(duplicates):
        del items[index]


def harden(repo_root: Path = ROOT) -> bool:
    reviews_path = repo_root / "glossary" / "terminology_reviews.json"
    reviews = _load(reviews_path, {"schema_version": 1, "decisions": []})
    decisions = reviews.setdefault("decisions", [])
    if not isinstance(decisions, list):
        raise ValueError("glossary/terminology_reviews.json decisions must be a list")
    before = json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    _upsert_unique(decisions, DECISION, "decision_id")
    after = json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    if before == after:
        return False
    _write(reviews_path, reviews)
    return True


def main() -> int:
    changed = harden(ROOT)
    print(f"rushed_prose_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

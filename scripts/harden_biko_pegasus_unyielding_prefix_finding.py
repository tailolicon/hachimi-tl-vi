from __future__ import annotations

"""Resolve the Unyielding Vow family-prefix finding without collapsing exact variants."""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "不可动摇的热血誓言"

DECISION = {
    "decision_id": "audit.finding.condition-biko-pegasus-unyielding-vow-prefix",
    "source_zh_cn": SOURCE,
    "action": "ignore",
    "kind": "context_rule",
    "category": "condition",
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [["142"]],
    "match_mode": "contains",
    "note": (
        "This worker-reported source is a lexical prefix shared by the exact Biko Pegasus Conditions "
        "不可动摇的热血誓言・短距离 and 不可动摇的热血誓言・英里. Those full labels are already canonically "
        "locked as Unyielding Vow - Sprint and Unyielding Vow - Mile by the Biko Pegasus vow hardener. "
        "There is no standalone player-facing Condition represented by this prefix, so treating it as an "
        "independent canonical term would reintroduce the substring-family conflict. Ignore only this finding "
        "scope and preserve the exact full-label locks."
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
    reviews_path = repo_root / "glossary" / "terminology_reviews.json"
    reviews = _load(reviews_path, {"schema_version": 1, "decisions": []})
    decisions = reviews.setdefault("decisions", [])
    if not isinstance(decisions, list):
        raise ValueError("glossary/terminology_reviews.json decisions must be a list")

    before = json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    _upsert(decisions, DECISION, "decision_id")
    after = json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    if before == after:
        return False
    _write(reviews_path, reviews)
    return True


def main() -> int:
    changed = harden(ROOT)
    print(f"biko_pegasus_unyielding_prefix_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

"""Canonicalize Espoir City's named song 看我不把你整得头冒金星！."""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FINDING_ID = "cf-d3f7dc3b11c9e480"
SOURCE_ZH = "看我不把你整得头冒金星！"
SOURCE_JA = "ピヨっピヨにしてやんよッ！"
TARGET = "Peep Peep Pow!"
RULE_ID = "song.peep_peep_pow"
DECISION_ID = "audit.finding.song-peep-peep-pow"

RULE = {
    "id": RULE_ID,
    "category": "song",
    "source_aliases": [SOURCE_ZH],
    "preferred": TARGET,
    "compact": [],
    "accepted": [TARGET],
    "forbidden": [SOURCE_ZH, "Xem tôi có đánh cho bạn hoa mắt không nào!"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "match_mode": "exact",
    "basis": (
        "The live zh-CN title 看我不把你整得头冒金星！ maps to Espoir City's WINNING LIVE 23 song "
        "ピヨっピヨにしてやんよッ！. Lantis-distributed English storefront/catalog metadata publishes the track as "
        "Peep Peep Pow!. Preserve that stable English-facing proper-name identity instead of the semantic "
        "Vietnamese rendering. Exact matching prevents generic threat/impact prose from being canonicalized."
    ),
}

DECISION = {
    "decision_id": DECISION_ID,
    "source_zh_cn": SOURCE_ZH,
    "action": "lock",
    "target_vi": TARGET,
    "kind": "proper_name",
    "category": "song",
    "ja": [SOURCE_JA],
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "match_mode": "exact",
    "note": (
        "The zh-CN title corresponds to Espoir City's WINNING LIVE 23 song ピヨっピヨにしてやんよッ！; "
        "lock the Lantis-distributed English catalog title Peep Peep Pow!."
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
    _upsert(community.setdefault("terms", []), RULE, "id")
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

    findings_path = repo_root / "glossary" / "canonical_findings.json"
    findings = _load(findings_path, {"schema_version": 1, "findings": []})
    before = json.dumps(findings, ensure_ascii=False, sort_keys=True)
    found = False
    for finding in findings.get("findings", []):
        if not isinstance(finding, dict) or finding.get("finding_id") != FINDING_ID:
            continue
        found = True
        suggestions = [str(value) for value in finding.get("suggested_targets_vi", []) if str(value)]
        if TARGET not in suggestions:
            suggestions.append(TARGET)
        finding["suggested_targets_vi"] = suggestions
        break
    if not found:
        raise ValueError(f"missing canonical finding {FINDING_ID}")
    if before != json.dumps(findings, ensure_ascii=False, sort_keys=True):
        _write(findings_path, findings)
        changed = True

    return changed


def main() -> int:
    changed = harden(ROOT)
    print(f"peep_peep_pow_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

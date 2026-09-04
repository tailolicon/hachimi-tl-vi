from __future__ import annotations

"""Canonicalize the named song トレセン音頭.

The companion regression is committed before this validation touch so the
production workflows evaluate one SHA containing both hardener and tests.
"""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FINDING_ID = "cf-5c83fe60c17ea214"
SOURCE = "トレセン音頭"
TARGET = "Tracen Ondo"
RULE_ID = "song.tracen_ondo"
DECISION_ID = "audit.finding.song-tracen-ondo"

RULE = {
    "id": RULE_ID,
    "category": "song",
    "source_aliases": [SOURCE],
    "preferred": TARGET,
    "compact": [],
    "accepted": [TARGET],
    "forbidden": [SOURCE, "Điệu ondo Tracen"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "match_mode": "exact",
    "basis": (
        "Official Lantis WINNING LIVE 13 lists トレセン音頭 as the Uma Musume 2.5th-anniversary song. "
        "English-facing music catalogs for the same Lantis release identify it as Tracen Ondo. Preserve "
        "the established Latin/Romanized song identity instead of the semantic Vietnamese title. Exact "
        "matching prevents the song lock from leaking into prose."
    ),
}

DECISION = {
    "decision_id": DECISION_ID,
    "source_zh_cn": SOURCE,
    "action": "lock",
    "target_vi": TARGET,
    "kind": "proper_name",
    "category": "song",
    "ja": [SOURCE],
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "match_mode": "exact",
    "note": (
        "Named 2.5th-anniversary song on Lantis WINNING LIVE 13; lock the established title "
        "Tracen Ondo rather than semantically translating 音頭."
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
    print(f"tracen_ondo_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

"""Canonicalize the named remix Make debut! (モリシー (Awesome City Club) Remix)."""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FINDING_ID = "cf-5f39dad6eabba899"
SOURCE = "Make debut! (モリシー (Awesome City Club) Remix)"
TARGET = "Make debut! (Morishi (Awesome City Club) Remix)"
RULE_ID = "song.make_debut_morishi_remix"
DECISION_ID = "audit.finding.song-make-debut-morishi-remix"

RULE = {
    "id": RULE_ID,
    "category": "song",
    "source_aliases": [SOURCE],
    "preferred": TARGET,
    "compact": [],
    "accepted": [TARGET],
    "forbidden": [SOURCE],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "match_mode": "exact",
    "basis": (
        "Official Lantis WINNING LIVE Remix ALBUM Paka Age Mix Vol.1 lists the exact remix title with "
        "モリシー (Awesome City Club). Established English-facing Uma Musume discography references render the "
        "remixer name as Morishi. Preserve the full Latin title Make debut! (Morishi (Awesome City Club) Remix). "
        "Exact matching prevents the proper-name lock from leaking into unrelated creator-name prose."
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
        "Named remix from the official WINNING LIVE Remix ALBUM; lock the established Latin spelling Morishi "
        "inside the complete track title instead of leaving Japanese-script creator-name leakage."
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
    print(f"make_debut_morishi_remix_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

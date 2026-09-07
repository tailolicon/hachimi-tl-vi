from __future__ import annotations

"""Canonicalize Rhein Kraft's Character Piece label and shield 力量 from stat matching."""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FINDING_ID = "cf-539366af08a7a714"
SOURCE_ZH = "莱茵力量的碎片"
TARGET = "Mảnh của Rhein Kraft"
RULE_ID = "character_piece.rhein_kraft"
DECISION_ID = "audit.finding.character-piece-rhein-kraft"

RULE = {
    "id": RULE_ID,
    "category": "character_piece_label",
    "source_aliases": [SOURCE_ZH],
    "preferred": TARGET,
    "compact": [],
    "accepted": [TARGET],
    "forbidden": [],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [["113"]],
    "match_mode": "exact",
    "basis": (
        "characters.json and character.rhein_kraft canonically identify 莱茵力量 as Rhein Kraft. "
        "In text_data category 113 this exact source is the Character Piece label, so 力量 is part "
        "of the proper name rather than the Power stat. Preserve the already-correct Vietnamese label."
    ),
}

DECISION = {
    "decision_id": DECISION_ID,
    "source_zh_cn": SOURCE_ZH,
    "action": "lock",
    "target_vi": TARGET,
    "kind": "context_rule",
    "category": "character_piece_label",
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [["113"]],
    "match_mode": "exact",
    "note": (
        "Rhein Kraft Character Piece label. character.rhein_kraft is authoritative; the embedded "
        "力量 must not trigger the generic Power-stat matcher in category 113."
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
        _write(community_path, community); changed = True

    reviews_path = repo_root / "glossary" / "terminology_reviews.json"
    reviews = _load(reviews_path, {"schema_version": 1, "decisions": []})
    before = json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    _upsert(reviews.setdefault("decisions", []), DECISION, "decision_id")
    if before != json.dumps(reviews, ensure_ascii=False, sort_keys=True):
        _write(reviews_path, reviews); changed = True

    findings_path = repo_root / "glossary" / "canonical_findings.json"
    findings = _load(findings_path, {"schema_version": 1, "findings": []})
    before = json.dumps(findings, ensure_ascii=False, sort_keys=True)
    found = False
    for finding in findings.get("findings", []):
        if isinstance(finding, dict) and finding.get("finding_id") == FINDING_ID:
            found = True
            suggestions = [str(v) for v in finding.get("suggested_targets_vi", []) if str(v)]
            if TARGET not in suggestions: suggestions.append(TARGET)
            finding["suggested_targets_vi"] = suggestions
            break
    if not found:
        raise ValueError(f"missing canonical finding {FINDING_ID}")
    if before != json.dumps(findings, ensure_ascii=False, sort_keys=True):
        _write(findings_path, findings); changed = True
    return changed


def main() -> int:
    print(f"rhein_kraft_character_piece_changed={str(harden(ROOT)).lower()}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

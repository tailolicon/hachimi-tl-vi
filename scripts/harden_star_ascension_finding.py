from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "才能开花"
REVIEWED_TERM_ID = "reviewed.system_label.b91773563cec"
LEGACY_TARGET = "Talent Bloom"
CANONICAL_TARGET = "Star Ascension"
MIGRATION_NOTE = "Canonical hardening: migrated legacy Talent Bloom label to released Global Star Ascension."

STAR_ASCENSION = {
    "id": "system.star_ascension.character_piece_description",
    "category": "progression",
    "source_aliases": [SOURCE],
    "preferred": CANONICAL_TARGET,
    "compact": [],
    "accepted": [CANONICAL_TARGET],
    "forbidden": ["Nở rộ tài năng", "Khai hoa tài năng"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [["114"]],
    "match_mode": "contains",
    "basis": "Named trainee progression mechanic. JP 才能開花 consumes Character Pieces to raise a trainee's star rarity; released Global player-facing terminology uses Star Ascension. Scope is restricted to text_data category 114 Character Piece descriptions so the separate Skill title 开花 and generic bloom/talent prose are unaffected.",
}

STAR_ASCENSION_DECISION = {
    "decision_id": "audit.finding.system-star-ascension",
    "source_zh_cn": SOURCE,
    "action": "lock",
    "target_vi": CANONICAL_TARGET,
    "kind": "system_label",
    "category": "progression",
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [["114"]],
    "match_mode": "contains",
    "note": "JP 才能開花 is the Character Piece star-rarity progression mechanic; preserve released Global player-facing label Star Ascension in category-114 Character Piece descriptions.",
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


def _append_migration_note(record: dict[str, Any]) -> None:
    note = str(record.get("note") or "").strip()
    if MIGRATION_NOTE not in note:
        record["note"] = f"{note} {MIGRATION_NOTE}".strip()


def _migrate_legacy_registry_lock(registry: dict[str, Any]) -> bool:
    changed = False
    for term in registry.get("terms", []):
        if not isinstance(term, dict) or str(term.get("id") or "") != REVIEWED_TERM_ID:
            continue
        if not bool(term.get("locked")):
            raise ValueError(f"{REVIEWED_TERM_ID} exists but is not locked")
        target = str(term.get("target_vi") or "")
        if target == LEGACY_TARGET:
            term["target_vi"] = CANONICAL_TARGET
            _append_migration_note(term)
            changed = True
        elif target != CANONICAL_TARGET:
            raise ValueError(
                f"{REVIEWED_TERM_ID} maps to unexpected target {target!r}; expected {LEGACY_TARGET!r} or {CANONICAL_TARGET!r}"
            )
        break
    return changed


def _migrate_legacy_review_decisions(reviews: dict[str, Any]) -> bool:
    changed = False
    for decision in reviews.get("decisions", []):
        if not isinstance(decision, dict):
            continue
        if str(decision.get("action") or "").strip().lower() != "lock":
            continue
        if str(decision.get("source_zh_cn") or "").strip() != SOURCE:
            continue
        if str(decision.get("kind") or "").strip().lower() != "system_label":
            continue
        target = str(decision.get("target_vi") or "")
        if target == LEGACY_TARGET:
            decision["target_vi"] = CANONICAL_TARGET
            _append_migration_note(decision)
            changed = True
        elif target != CANONICAL_TARGET:
            raise ValueError(
                f"review decision {decision.get('decision_id')!r} for {SOURCE} maps to unexpected target {target!r}"
            )
    return changed


def harden(repo_root: Path = ROOT) -> bool:
    changed = False

    # Context Sync applies reviewed locks before the normal hardener sweep. The
    # stable reviewed id for 才能开花 already existed with the legacy Talent
    # Bloom wording, and an older reviewed decision carried the same target.
    # Migrate both authoritative surfaces explicitly so safe review application
    # can remain strict instead of silently rewriting an existing lock.
    registry_path = repo_root / "glossary" / "term_registry.json"
    registry = _load(registry_path, {"terms": []})
    before = json.dumps(registry, ensure_ascii=False, sort_keys=True)
    _migrate_legacy_registry_lock(registry)
    if before != json.dumps(registry, ensure_ascii=False, sort_keys=True):
        _write(registry_path, registry)
        changed = True

    reviews_path = repo_root / "glossary" / "terminology_reviews.json"
    reviews = _load(reviews_path, {"schema_version": 1, "decisions": []})
    before = json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    _migrate_legacy_review_decisions(reviews)
    _upsert(reviews.setdefault("decisions", []), STAR_ASCENSION_DECISION, "decision_id")
    if before != json.dumps(reviews, ensure_ascii=False, sort_keys=True):
        _write(reviews_path, reviews)
        changed = True

    community_path = repo_root / "glossary" / "ui_community_terms.json"
    community = _load(community_path, {"schema_version": 1, "terms": []})
    before = json.dumps(community, ensure_ascii=False, sort_keys=True)
    _upsert(community.setdefault("terms", []), STAR_ASCENSION, "id")
    if before != json.dumps(community, ensure_ascii=False, sort_keys=True):
        _write(community_path, community)
        changed = True

    return changed


def main() -> int:
    changed = harden(ROOT)
    print(f"star_ascension_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

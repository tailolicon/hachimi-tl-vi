from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

SHADOW_ROLL = {
    "id": "song.shadow_roll_no_chikai_the_solid_revision",
    "category": "song",
    "source_aliases": ["シャドーロールの誓い（The Solid Revision）"],
    "preferred": "Shadow Roll no Chikai (The Solid Revision)",
    "compact": [],
    "accepted": ["Shadow Roll no Chikai (The Solid Revision)"],
    "forbidden": ["Lời thề Shadow Roll (The Solid Revision)", "Vow of Shadow Roll (The Solid Revision)"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [["16"]],
    "match_mode": "exact",
    "basis": "Named song title シャドーロールの誓い（The Solid Revision）. Preserve the stable Romanized Japanese identity Shadow Roll no Chikai together with the title's existing English parenthetical, avoiding an unverified semantic English/Vietnamese translation.",
}

SHADOW_ROLL_DECISION = {
    "decision_id": "audit.finding.song-shadow-roll-no-chikai",
    "source_zh_cn": "シャドーロールの誓い（The Solid Revision）",
    "action": "lock",
    "target_vi": "Shadow Roll no Chikai (The Solid Revision)",
    "kind": "proper_name",
    "category": "song",
    "note": "Preserve the verified Romanized Japanese title plus its original English parenthetical rather than inventing a translated proper title.",
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
    changed = False
    community_path = repo_root / "glossary" / "ui_community_terms.json"
    community = _load(community_path, {"schema_version": 1, "terms": []})
    terms = community.setdefault("terms", [])
    if not isinstance(terms, list):
        raise ValueError("glossary/ui_community_terms.json terms must be a list")
    before = json.dumps(community, ensure_ascii=False, sort_keys=True)
    _upsert(terms, SHADOW_ROLL, id_field="id")
    if before != json.dumps(community, ensure_ascii=False, sort_keys=True):
        _write(community_path, community)
        changed = True

    reviews_path = repo_root / "glossary" / "terminology_reviews.json"
    reviews = _load(reviews_path, {"schema_version": 1, "decisions": []})
    decisions = reviews.setdefault("decisions", [])
    if not isinstance(decisions, list):
        raise ValueError("glossary/terminology_reviews.json decisions must be a list")
    before = json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    _upsert(decisions, SHADOW_ROLL_DECISION, id_field="decision_id")
    if before != json.dumps(reviews, ensure_ascii=False, sort_keys=True):
        _write(reviews_path, reviews)
        changed = True
    return changed


def main() -> int:
    changed = harden(ROOT)
    print(f"shadow_roll_song_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

SORA_NO_HOHOEMI = {
    "id": "song.why_the_sky_makes_me_smile",
    "category": "song",
    "source_aliases": ["空のほほえみ方"],
    "preferred": "Why the Sky Makes Me Smile",
    "compact": [],
    "accepted": ["Why the Sky Makes Me Smile"],
    "forbidden": ["Cách bầu trời mỉm cười"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [["16"]],
    "match_mode": "exact",
    "basis": "Named Kitasan Black solo song 空のほほえみ方. Current international Uma Musume reference identifies the English title as Why the Sky Makes Me Smile; preserve that proper-title identity instead of a Vietnamese semantic calque.",
}

SORA_NO_HOHOEMI_DECISION = {
    "decision_id": "audit.finding.song-why-the-sky-makes-me-smile",
    "source_zh_cn": "空のほほえみ方",
    "action": "lock",
    "target_vi": "Why the Sky Makes Me Smile",
    "kind": "proper_name",
    "category": "song",
    "note": "Verified international title for Kitasan Black's 空のほほえみ方; preserve Why the Sky Makes Me Smile in the song-title table.",
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
    _upsert(terms, SORA_NO_HOHOEMI, id_field="id")
    if before != json.dumps(community, ensure_ascii=False, sort_keys=True):
        _write(community_path, community)
        changed = True

    reviews_path = repo_root / "glossary" / "terminology_reviews.json"
    reviews = _load(reviews_path, {"schema_version": 1, "decisions": []})
    decisions = reviews.setdefault("decisions", [])
    if not isinstance(decisions, list):
        raise ValueError("glossary/terminology_reviews.json decisions must be a list")
    before = json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    _upsert(decisions, SORA_NO_HOHOEMI_DECISION, id_field="decision_id")
    if before != json.dumps(reviews, ensure_ascii=False, sort_keys=True):
        _write(reviews_path, reviews)
        changed = True
    return changed


def main() -> int:
    changed = harden(ROOT)
    print(f"sora_no_hohoemi_song_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

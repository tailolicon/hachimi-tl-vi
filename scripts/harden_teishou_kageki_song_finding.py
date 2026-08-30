from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

TEISHOU_KAGEKI = {
    "id": "song.teishou_kageki_tataeyo_towa_ni",
    "category": "song",
    "source_aliases": ["帝笑歌劇〜讃えよ永久に〜"],
    "preferred": "Teishou Kageki ~Tataeyo Towa ni~",
    "compact": [],
    "accepted": ["Teishou Kageki ~Tataeyo Towa ni~"],
    "forbidden": ["Đế Tiếu Ca Kịch ~Hãy ca tụng mãi mãi~", "Ca kịch Đế Tiếu ~Hãy ca tụng vĩnh viễn~"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [["16"]],
    "match_mode": "exact",
    "basis": "Named T.M. Opera O solo song 帝笑歌劇〜讃えよ永久に〜. Current international Uma Musume references expose the stable Romanized identity Teishou Kageki ~Tataeyo Towa ni~; preserve that proper title rather than a Vietnamese semantic calque.",
}

TEISHOU_KAGEKI_DECISION = {
    "decision_id": "audit.finding.song-teishou-kageki-tataeyo-towa-ni",
    "source_zh_cn": "帝笑歌劇〜讃えよ永久に〜",
    "action": "lock",
    "target_vi": "Teishou Kageki ~Tataeyo Towa ni~",
    "kind": "proper_name",
    "category": "song",
    "note": "Verified Romanized identity for T.M. Opera O's 帝笑歌劇〜讃えよ永久に〜; preserve Teishou Kageki ~Tataeyo Towa ni~ in the song-title table.",
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
    _upsert(terms, TEISHOU_KAGEKI, id_field="id")
    if before != json.dumps(community, ensure_ascii=False, sort_keys=True):
        _write(community_path, community)
        changed = True

    reviews_path = repo_root / "glossary" / "terminology_reviews.json"
    reviews = _load(reviews_path, {"schema_version": 1, "decisions": []})
    decisions = reviews.setdefault("decisions", [])
    if not isinstance(decisions, list):
        raise ValueError("glossary/terminology_reviews.json decisions must be a list")
    before = json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    _upsert(decisions, TEISHOU_KAGEKI_DECISION, id_field="decision_id")
    if before != json.dumps(reviews, ensure_ascii=False, sort_keys=True):
        _write(reviews_path, reviews)
        changed = True
    return changed


def main() -> int:
    changed = harden(ROOT)
    print(f"teishou_kageki_song_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

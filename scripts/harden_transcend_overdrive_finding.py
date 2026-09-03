from __future__ import annotations

"""Canonicalize Transcend's 地熱解放オーヴァードライブ unique Skill."""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ZH = "地热解放超驱动"
SOURCE_JA = "地熱解放オーヴァードライブ"
PREFERRED = "Giải phóng địa nhiệt Overdrive"
TERM_ID = "skill.transcend.geothermal_release_overdrive"

TERM = {
    "id": TERM_ID,
    "category": "skill_name",
    "source_aliases": [SOURCE_ZH],
    "preferred": PREFERRED,
    "compact": [],
    "accepted": [PREFERRED],
    "forbidden": ["Siêu tăng tốc giải phóng địa nhiệt"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [["147"]],
    "match_mode": "exact",
    "basis": (
        "Character/card ID 108002 is Transcend [宵闇ネオカグラ], whose verified JP unique Skill is "
        "地熱解放オーヴァードライブ. The zh-CN bridge 地热解放超驱动 semantically replaces the named "
        "katakana element オーヴァードライブ, while the older Vietnamese text flattens it to generic "
        "'Siêu tăng tốc'. Preserve the distinctive Overdrive identity and render 地熱解放 directly as "
        "'giải phóng địa nhiệt'. This exact wording reuses the repository's pre-existing locked term "
        "skill.110801 rather than introducing a conflicting duplicate canonical."
    ),
}

DECISION = {
    "decision_id": "audit.finding.skill-transcend-overdrive",
    "source_zh_cn": SOURCE_ZH,
    "action": "lock",
    "target_vi": PREFERRED,
    "kind": "skill_name",
    "category": "skill_name",
    "ja": [SOURCE_JA],
    "note": (
        "Verified JP identity 地熱解放オーヴァードライブ for Transcend [宵闇ネオカグラ] preserves the "
        "named Overdrive element lost by the zh-CN/Vietnamese semantic calque. Reuse the already locked "
        "project canonical 'Giải phóng địa nhiệt Overdrive'; do not create a second ordering variant or "
        "present it as an official Global title."
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
    _upsert(terms, TERM, id_field="id")
    if before != json.dumps(community, ensure_ascii=False, sort_keys=True):
        _write(community_path, community)
        changed = True

    reviews_path = repo_root / "glossary" / "terminology_reviews.json"
    reviews = _load(reviews_path, {"schema_version": 1, "decisions": []})
    decisions = reviews.setdefault("decisions", [])
    if not isinstance(decisions, list):
        raise ValueError("glossary/terminology_reviews.json decisions must be a list")
    before = json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    _upsert(decisions, DECISION, id_field="decision_id")
    if before != json.dumps(reviews, ensure_ascii=False, sort_keys=True):
        _write(reviews_path, reviews)
        changed = True
    return changed


def main() -> int:
    changed = harden(ROOT)
    print(f"transcend_overdrive_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

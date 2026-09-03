from __future__ import annotations

"""Canonicalize Copano Rickey's 五獣挙りて彩光奏づ unique Skill.

The zh-CN bridge `五行之兽彩光合奏` materially rewrites the JP motif: `五獣`
means five beasts, not beasts of the Five Elements. Preserve the verified JP
identity and use a compact Vietnamese literary title instead of carrying that
bridge invention into the canonical target.
"""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FINDING_ID = "cf-078ae8e41d26c58b"
SOURCE_ZH = "五行之兽彩光合奏"
SOURCE_JA = "五獣挙りて彩光奏づ"
PREFERRED = "Ngũ Thú Tề Tựu, Tấu Khúc Sắc Quang"

FIVE_BEASTS_COLORED_LIGHT = {
    "id": "skill.copano_rickey.five_beasts_colored_light",
    "category": "skill_name",
    "source_aliases": [SOURCE_ZH],
    "preferred": PREFERRED,
    "compact": [],
    "accepted": [PREFERRED],
    "forbidden": ["Hợp tấu ánh sắc của Ngũ Hành Thú"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "match_mode": "exact",
    "basis": (
        "Repository keys 10980201-10980203 map the zh-CN title 五行之兽彩光合奏 "
        "to JP unique Skill 五獣挙りて彩光奏づ for Copano Rickey [光彩陸離☆招福衣]. "
        "The JP 五獣 motif is simply five beasts; the zh-CN bridge adds unsupported "
        "Five-Elements imagery. Restore that identity as Ngũ Thú and keep the "
        "remaining literary image compact as Tề Tựu, Tấu Khúc Sắc Quang."
    ),
}

FIVE_BEASTS_COLORED_LIGHT_DECISION = {
    "decision_id": "audit.finding.skill-copano-rickey-five-beasts-colored-light",
    "source_zh_cn": SOURCE_ZH,
    "action": "lock",
    "target_vi": PREFERRED,
    "kind": "skill_name",
    "category": "skill_name",
    "ja": [SOURCE_JA],
    "note": (
        "Verified JP identity is 五獣挙りて彩光奏づ. The zh-CN bridge rewrites 五獣 "
        "as 五行之兽, so the old Vietnamese Ngũ Hành Thú wording is source-bridge "
        "leakage rather than the original Skill motif. Lock the JP-guarded compact "
        "Vietnamese title instead."
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
    _upsert(terms, FIVE_BEASTS_COLORED_LIGHT, id_field="id")
    if before != json.dumps(community, ensure_ascii=False, sort_keys=True):
        _write(community_path, community)
        changed = True

    reviews_path = repo_root / "glossary" / "terminology_reviews.json"
    reviews = _load(reviews_path, {"schema_version": 1, "decisions": []})
    decisions = reviews.setdefault("decisions", [])
    if not isinstance(decisions, list):
        raise ValueError("glossary/terminology_reviews.json decisions must be a list")
    before = json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    _upsert(decisions, FIVE_BEASTS_COLORED_LIGHT_DECISION, id_field="decision_id")
    if before != json.dumps(reviews, ensure_ascii=False, sort_keys=True):
        _write(reviews_path, reviews)
        changed = True

    return changed


def main() -> int:
    changed = harden(ROOT)
    print(f"copano_rickey_five_beasts_colored_light_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

"""Canonicalize Air Messiah's 辿る血脈、芽吹く未来 unique Skill.

The zh-CN bridge `相依血脉,开花未来` changes two important images from the
verified JP title: 辿る is following/tracing a bloodline, and 芽吹く is budding
or sprouting rather than an already-bloomed future. Preserve the JP identity in
a compact Vietnamese game title instead of canonizing the literal zh-CN bridge.
"""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FINDING_ID = "cf-9d142519bc912d1b"
SOURCE_ZH = "相依血脉,开花未来"
SOURCE_JA = "辿る血脈、芽吹く未来"
PREFERRED = "Theo Dấu Huyết Mạch, Tương Lai Nảy Mầm"

AIR_MESSIAH_BLOODLINE_FUTURE = {
    "id": "skill.air_messiah.bloodline_future",
    "category": "skill_name",
    "source_aliases": [SOURCE_ZH],
    "preferred": PREFERRED,
    "compact": [],
    "accepted": [PREFERRED],
    "forbidden": ["Huyết mạch nương tựa, tương lai Nở rộ"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "match_mode": "exact",
    "basis": (
        "Repository keys 11110101-11110103 map zh-CN 相依血脉,开花未来 to "
        "Air Messiah's JP unique Skill 辿る血脈、芽吹く未来. Independent JP data "
        "identifies the same title and effect, while English-facing data still marks "
        "the Skill JP-only. Follow the repository skill-name style policy: use the "
        "zh-CN title for compact rhythm but JP as the semantic guard. Theo Dấu Huyết "
        "Mạch preserves 辿る血脈, and Tương Lai Nảy Mầm preserves 芽吹く未来 instead "
        "of the zh-CN bridge's different dependence/blooming imagery."
    ),
}

AIR_MESSIAH_BLOODLINE_FUTURE_DECISION = {
    "decision_id": "audit.finding.skill-air-messiah-bloodline-future",
    "source_zh_cn": SOURCE_ZH,
    "action": "lock",
    "target_vi": PREFERRED,
    "kind": "skill_name",
    "category": "skill_name",
    "ja": [SOURCE_JA],
    "note": (
        "Verified identity is Air Messiah's JP unique Skill 辿る血脈、芽吹く未来. "
        "The zh-CN bridge changes 辿る to 相依 and 芽吹く to 开花, so preserve the "
        "JP motifs as Theo Dấu Huyết Mạch, Tương Lai Nảy Mầm."
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
    _upsert(terms, AIR_MESSIAH_BLOODLINE_FUTURE, id_field="id")
    if before != json.dumps(community, ensure_ascii=False, sort_keys=True):
        _write(community_path, community)
        changed = True

    reviews_path = repo_root / "glossary" / "terminology_reviews.json"
    reviews = _load(reviews_path, {"schema_version": 1, "decisions": []})
    decisions = reviews.setdefault("decisions", [])
    if not isinstance(decisions, list):
        raise ValueError("glossary/terminology_reviews.json decisions must be a list")
    before = json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    _upsert(decisions, AIR_MESSIAH_BLOODLINE_FUTURE_DECISION, id_field="decision_id")
    if before != json.dumps(reviews, ensure_ascii=False, sort_keys=True):
        _write(reviews_path, reviews)
        changed = True

    return changed


def main() -> int:
    changed = harden(ROOT)
    print(f"air_messiah_bloodline_future_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

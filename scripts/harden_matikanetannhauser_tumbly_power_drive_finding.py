from __future__ import annotations

"""Canonicalize Matikanetannhauser (Blue Turbulence)'s ごろりん！？パワードライブ unique Skill."""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FINDING_ID = "cf-51acc67fc17560ad"
SOURCE_ZH = "车轮滚滚！？动力驱动"
SOURCE_JA = "ごろりん！？パワードライブ"
PREFERRED = "Lăn Tròn!? Power Drive"
TERM_ID = "skill.matikanetannhauser.tumbly_power_drive"

TERM = {
    "id": TERM_ID,
    "category": "skill_name",
    "source_aliases": [SOURCE_ZH],
    "preferred": PREFERRED,
    "compact": [],
    "accepted": [PREFERRED],
    "forbidden": ["Bánh xe lăn bánh!? Truyền động mạnh mẽ"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "match_mode": "contains",
    "basis": (
        "Repository inheritance-factor keys 10620201-10620203 belong to the Blue Turbulence "
        "Matikanetannhauser trainee. Current JP references identify her unique Skill exactly as "
        "ごろりん！？パワードライブ. The playful ごろりん is a tumbling/rolling expression, while "
        "パワードライブ is the stylized mechanical phrase Power Drive. Following skill_name_style, "
        "Lăn Tròn!? Power Drive keeps the short playful rhythm and mechanical loan phrase instead of "
        "the longer historical zh-CN calque."
    ),
}

DECISION = {
    "decision_id": "audit.finding.skill-matikanetannhauser-tumbly-power-drive",
    "source_zh_cn": SOURCE_ZH,
    "action": "lock",
    "target_vi": PREFERRED,
    "kind": "skill_name",
    "category": "skill_name",
    "ja": [SOURCE_JA],
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "match_mode": "contains",
    "note": (
        "Verified JP identity is Blue Turbulence Matikanetannhauser's unique Skill "
        "ごろりん！？パワードライブ. Use the compact Vietnamese title Lăn Tròn!? Power Drive "
        "for the Skill title embedded in inheritance-factor prose."
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
    print(f"matikanetannhauser_tumbly_power_drive_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

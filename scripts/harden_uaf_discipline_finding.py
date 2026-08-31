from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

DISCIPLINES = (
    ("机枪接球", "Machine Gun Receive", "machine_gun_receive"),
    ("巨山灌篮", "Mountain Dunk", "mountain_dunk"),
    ("摔柔移山", "Push the Rock", "push_the_rock"),
    ("打桩推手", "Harite Pile", "harite_pile"),
    ("千兆摔投", "Gigantic Throw", "gigantic_throw"),
    ("悬挂攀岩", "Hang Climb", "hang_climb"),
    ("潜艇屏息", "Like a Submarine", "like_a_submarine"),
    ("特技箭道", "Acrobat Arrow", "acrobat_arrow"),
)


def _term(source: str, target: str, slug: str) -> dict[str, Any]:
    return {
        "id": f"scenario.uaf.discipline.{slug}",
        "category": "system_label",
        "source_aliases": [source],
        "preferred": target,
        "compact": [],
        "accepted": [target],
        "forbidden": [],
        "require_accepted": True,
        "invalidation_scope": "item",
        "source_paths": ["localize_dict.json"],
        "match_mode": "exact",
        "basis": "Named U.A.F. Ready GO! sports discipline. Preserve the established English player-facing/community discipline title rather than literalizing the zh-CN localization.",
    }


def _decision(source: str, target: str, slug: str) -> dict[str, Any]:
    return {
        "decision_id": f"audit.finding.uaf-discipline-{slug}",
        "source_zh_cn": source,
        "action": "lock",
        "target_vi": target,
        "kind": "system_label",
        "category": "system_label",
        "note": "Verified U.A.F. discipline title against the JP discipline list and established GameTora English naming.",
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


def _upsert(items: list[Any], record: dict[str, Any], field: str) -> None:
    rid = str(record[field])
    for index, item in enumerate(items):
        if isinstance(item, dict) and str(item.get(field) or "") == rid:
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
        raise ValueError("community terms must be a list")
    before = json.dumps(community, ensure_ascii=False, sort_keys=True)
    for source, target, slug in DISCIPLINES:
        _upsert(terms, _term(source, target, slug), "id")
    if before != json.dumps(community, ensure_ascii=False, sort_keys=True):
        _write(community_path, community)
        changed = True

    reviews_path = repo_root / "glossary" / "terminology_reviews.json"
    reviews = _load(reviews_path, {"schema_version": 1, "decisions": []})
    decisions = reviews.setdefault("decisions", [])
    if not isinstance(decisions, list):
        raise ValueError("review decisions must be a list")
    before = json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    for source, target, slug in DISCIPLINES:
        _upsert(decisions, _decision(source, target, slug), "decision_id")
    if before != json.dumps(reviews, ensure_ascii=False, sort_keys=True):
        _write(reviews_path, reviews)
        changed = True
    return changed


def main() -> int:
    print(f"uaf_discipline_hardening_changed={str(harden(ROOT)).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

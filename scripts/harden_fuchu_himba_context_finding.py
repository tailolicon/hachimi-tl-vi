from __future__ import annotations

"""Harden the fictional Fuchu Uma Musume Stakes proper name and its world-term guard."""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TERM_ID = "common.world.umamusume"
EXCLUSION = "府中赛马娘锦标"

FUCHU_UMA_MUSUME_STAKES = {
    "id": "race.fuchu_uma_musume_stakes.text131",
    "category": "race",
    "source_aliases": [EXCLUSION],
    "preferred": "Fuchu Uma Musume Stakes",
    "compact": [],
    "accepted": ["Fuchu Uma Musume Stakes"],
    "forbidden": ["Fuchu Himba Stakes", "府中赛马娘锦标"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [["131"]],
    "match_mode": "contains",
    "basis": "Verified in-game proper race name: zh-CN 府中赛马娘锦标 corresponds to JP 府中ウマ娘ステークス, the fictionalized in-game counterpart of the real-world Fuchu Himba Stakes. Preserve the game's Uma Musume wording as Fuchu Uma Musume Stakes and scope it to text_data category 131 objective/mission prose.",
}

FUCHU_UMA_MUSUME_STAKES_DECISION = {
    "decision_id": "audit.finding.fuchu-uma-musume-stakes",
    "source_zh_cn": EXCLUSION,
    "action": "lock",
    "target_vi": "Fuchu Uma Musume Stakes",
    "kind": "race_name",
    "category": "race",
    "note": "Verified against JP 府中ウマ娘ステークス. This is the in-game fictionalized race name, distinct from the real-world Fuchu Himba Stakes; generic 赛马娘/Mã Nương matching must remain excluded inside this proper name.",
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
    payload = _load(community_path, {"schema_version": 1, "terms": []})
    terms = payload.get("terms", [])
    if not isinstance(terms, list):
        raise ValueError("glossary/ui_community_terms.json terms must be a list")
    before = json.dumps(payload, ensure_ascii=False, sort_keys=True)

    matched = False
    for term in terms:
        if not isinstance(term, dict) or term.get("id") != TERM_ID:
            continue
        matched = True
        exclusions = [str(value) for value in term.get("exclude_source_contains", []) if str(value)]
        term["exclude_source_contains"] = list(dict.fromkeys([*exclusions, EXCLUSION]))
        term["basis"] = (
            "Generic 赛马娘 is the project world/species term Mã Nương, but it must not fire inside established proper race names such as 府中赛马娘锦标 (Fuchu Uma Musume Stakes)."
        )
        break
    if not matched:
        raise ValueError(f"missing canonical community term {TERM_ID}")

    _upsert(terms, FUCHU_UMA_MUSUME_STAKES, "id")
    if before != json.dumps(payload, ensure_ascii=False, sort_keys=True):
        _write(community_path, payload)
        changed = True

    reviews_path = repo_root / "glossary" / "terminology_reviews.json"
    reviews = _load(reviews_path, {"schema_version": 1, "decisions": []})
    decisions = reviews.setdefault("decisions", [])
    if not isinstance(decisions, list):
        raise ValueError("glossary/terminology_reviews.json decisions must be a list")
    before = json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    _upsert(decisions, FUCHU_UMA_MUSUME_STAKES_DECISION, "decision_id")
    if before != json.dumps(reviews, ensure_ascii=False, sort_keys=True):
        _write(reviews_path, reviews)
        changed = True

    return changed


def main() -> int:
    changed = harden(ROOT)
    print(f"fuchu_himba_context_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

OMINOUS_PORTENT = {
    "id": "condition.copano_rickey.ominous_portent",
    "category": "condition",
    "source_aliases": ["怪云行天"],
    "preferred": "Ominous Portent",
    "compact": [],
    "accepted": ["Ominous Portent"],
    "forbidden": ["Mây Lạ Lướt Trời"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [["142"]],
    "match_mode": "exact",
    "basis": "Verified Copano Rickey Condition identity: zh-CN 怪云行天 at text-data category 142/id 21 maps to JP 怪しい雲行き and current English player-facing name Ominous Portent. Keep the rule exact and confined to the Condition-name table because the zh-CN wording can also occur as ordinary prose/lyrics.",
}

OMINOUS_PORTENT_DECISION = {
    "decision_id": "audit.finding.condition-copano-rickey-ominous-portent",
    "source_zh_cn": "怪云行天",
    "action": "lock",
    "target_vi": "Ominous Portent",
    "kind": "condition",
    "category": "condition",
    "note": "Verified against JP 怪しい雲行き, Copano Rickey's special debuff Condition; use current English player-facing identity Ominous Portent and keep the lock scoped to the Condition-name table.",
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


def harden(repo_root: Path = ROOT) -> bool:
    changed = False

    community_path = repo_root / "glossary" / "ui_community_terms.json"
    community = _load(community_path, {"schema_version": 1, "terms": []})
    before = json.dumps(community, ensure_ascii=False, sort_keys=True)
    _upsert(community.setdefault("terms", []), OMINOUS_PORTENT, "id")
    if before != json.dumps(community, ensure_ascii=False, sort_keys=True):
        _write(community_path, community)
        changed = True

    reviews_path = repo_root / "glossary" / "terminology_reviews.json"
    reviews = _load(reviews_path, {"schema_version": 1, "decisions": []})
    before = json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    _upsert(reviews.setdefault("decisions", []), OMINOUS_PORTENT_DECISION, "decision_id")
    if before != json.dumps(reviews, ensure_ascii=False, sort_keys=True):
        _write(reviews_path, reviews)
        changed = True

    return changed


def main() -> int:
    changed = harden(ROOT)
    print(f"ominous_portent_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

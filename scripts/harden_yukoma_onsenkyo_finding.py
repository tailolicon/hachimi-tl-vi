from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

YUKOMA_ONSENKYO = {
    "id": "proper_name.yukoma_onsenkyo.scenario120",
    "category": "proper_name",
    "source_aliases": ["汤驹温泉乡"],
    "preferred": "Yukoma Onsenkyo",
    "compact": [],
    "accepted": ["Yukoma Onsenkyo"],
    "forbidden": ["汤驹温泉乡", "Làng suối nước nóng Yukoma"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [["120"]],
    "match_mode": "contains",
    "basis": "Named setting of the JP training scenario ごくらく♪ゆこま温泉郷. Cygames scenario coverage identifies the main facility/place as ゆこま温泉郷; preserve the distinctive proper name as Yukoma Onsenkyo rather than translating it as a generic hot-springs village. Scope is limited to scenario descriptions in text_data category 120.",
}

YUKOMA_ONSENKYO_DECISION = {
    "decision_id": "audit.finding.yukoma-onsenkyo",
    "source_zh_cn": "汤驹温泉乡",
    "action": "lock",
    "target_vi": "Yukoma Onsenkyo",
    "kind": "proper_name",
    "category": "proper_name",
    "note": "Verified against JP ゆこま温泉郷, the named main setting of the ごくらく♪ゆこま温泉郷 scenario; preserve the player-facing proper name as Yukoma Onsenkyo.",
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
    _upsert(terms, YUKOMA_ONSENKYO, id_field="id")
    if before != json.dumps(community, ensure_ascii=False, sort_keys=True):
        _write(community_path, community)
        changed = True

    reviews_path = repo_root / "glossary" / "terminology_reviews.json"
    reviews = _load(reviews_path, {"schema_version": 1, "decisions": []})
    decisions = reviews.setdefault("decisions", [])
    if not isinstance(decisions, list):
        raise ValueError("glossary/terminology_reviews.json decisions must be a list")
    before = json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    _upsert(decisions, YUKOMA_ONSENKYO_DECISION, id_field="decision_id")
    if before != json.dumps(reviews, ensure_ascii=False, sort_keys=True):
        _write(reviews_path, reviews)
        changed = True
    return changed


def main() -> int:
    changed = harden(ROOT)
    print(f"yukoma_onsenkyo_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

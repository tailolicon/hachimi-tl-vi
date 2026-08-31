from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

CASINO_DRIVE = {
    "id": "proper_name.casino_drive.scenario120",
    "category": "proper_name",
    "source_aliases": ["夺金旅途"],
    "preferred": "Casino Drive",
    "compact": [],
    "accepted": ["Casino Drive"],
    "forbidden": ["Stay Gold", "夺金旅途"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [["120"]],
    "match_mode": "contains",
    "basis": "Breeders' Cup DREAMS scenario identity. Official Cygames character page names カジノドライヴ as Casino Drive and describes her as the founder of the Breeders' Cup expedition project. The zh-CN scenario alias 夺金旅途 is therefore scoped to text_data category 120 so unrelated prose cannot inherit this proper-name mapping.",
}

CASINO_DRIVE_DECISION = {
    "decision_id": "audit.finding.casino-drive-scenario",
    "source_zh_cn": "夺金旅途",
    "action": "lock",
    "target_vi": "Casino Drive",
    "kind": "proper_name",
    "category": "proper_name",
    "note": "Verified against official Cygames Casino Drive / カジノドライヴ identity for the Breeders' Cup DREAMS scenario; replaces the incorrect Stay Gold rendering in this scoped scenario context.",
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
    _upsert(terms, CASINO_DRIVE, id_field="id")
    if before != json.dumps(community, ensure_ascii=False, sort_keys=True):
        _write(community_path, community)
        changed = True

    reviews_path = repo_root / "glossary" / "terminology_reviews.json"
    reviews = _load(reviews_path, {"schema_version": 1, "decisions": []})
    decisions = reviews.setdefault("decisions", [])
    if not isinstance(decisions, list):
        raise ValueError("glossary/terminology_reviews.json decisions must be a list")
    before = json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    _upsert(decisions, CASINO_DRIVE_DECISION, id_field="decision_id")
    if before != json.dumps(reviews, ensure_ascii=False, sort_keys=True):
        _write(reviews_path, reviews)
        changed = True
    return changed


def main() -> int:
    changed = harden(ROOT)
    print(f"casino_drive_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

"""Canonicalize Sirius Symboli's unique Skill セイリオス from zh-CN 天骄."""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ZH = "天骄"
SOURCE_JA = "セイリオス"
PREFERRED = "Seirios"
TERM_ID = "skill.sirius_symboli.seirios"

TERM = {
    "id": TERM_ID,
    "category": "skill_name",
    "source_aliases": [SOURCE_ZH],
    "preferred": PREFERRED,
    "compact": [],
    "accepted": [PREFERRED],
    "forbidden": ["Thiên kiêu"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "match_mode": "contains",
    "basis": (
        "Repository factor key 10700101 maps zh-CN 天骄 to JP セイリオス. Biligame's Umamusume factor page "
        "confirms that exact ID/title mapping, while international Umamusume reference data renders the JP-only "
        "unique Skill as Seirios for Sirius Symboli. Preserve the proper-title identity rather than the semantic zh-CN calque."
    ),
}

DECISION = {
    "decision_id": "audit.finding.skill-sirius-symboli-seirios",
    "source_zh_cn": SOURCE_ZH,
    "action": "lock",
    "target_vi": PREFERRED,
    "kind": "skill_name",
    "category": "skill_name",
    "ja": [SOURCE_JA],
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "match_mode": "contains",
    "note": "Verified factor ID 10700101 is Sirius Symboli's JP unique Skill セイリオス; international reference spelling is Seirios.",
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
    rid = str(record[id_field])
    for i, item in enumerate(items):
        if isinstance(item, dict) and str(item.get(id_field) or "") == rid:
            merged = dict(item); merged.update(record); items[i] = merged; return
    items.append(dict(record))


def harden(repo_root: Path = ROOT) -> bool:
    changed = False
    for filename, collection, record, id_field in [
        ("ui_community_terms.json", "terms", TERM, "id"),
        ("terminology_reviews.json", "decisions", DECISION, "decision_id"),
    ]:
        path = repo_root / "glossary" / filename
        payload = _load(path, {"schema_version": 1, collection: []})
        items = payload.setdefault(collection, [])
        if not isinstance(items, list): raise ValueError(f"{path} {collection} must be a list")
        before = json.dumps(payload, ensure_ascii=False, sort_keys=True)
        _upsert(items, record, id_field=id_field)
        if before != json.dumps(payload, ensure_ascii=False, sort_keys=True):
            _write(path, payload); changed = True
    return changed


def main() -> int:
    changed = harden(ROOT)
    print(f"seirios_skill_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

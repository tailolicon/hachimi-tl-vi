from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

TERM_ID = "world.umamusume.shorthand.schedulebook"
SOURCE_ZH = "马娘"
PREFERRED = "Mã Nương"
SCHEDULEBOOK_KEYS = [
    "ScheduleBook408021",
    "ScheduleBook408022",
    "ScheduleBook408061",
    "ScheduleBook408064",
    "ScheduleBook408065",
    "ScheduleBook408080",
]

UMAMUSUME_SHORTHAND_SCHEDULEBOOK = {
    "id": TERM_ID,
    "category": "world",
    "source_aliases": [SOURCE_ZH],
    "preferred": PREFERRED,
    "compact": [],
    "accepted": [PREFERRED],
    "forbidden": ["Uma Musume"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["localize_dict.json"],
    "key_exact": SCHEDULEBOOK_KEYS,
    "match_mode": "contains",
    "basis": (
        "The six evidence-bearing ScheduleBook UI strings use zh-CN 马娘 as the generic "
        "Umamusume world/species shorthand. Reuse the established Vietnamese term Mã Nương, "
        "but keep this short alias restricted to the reviewed ScheduleBook keys so unrelated "
        "proper-name or source-bridge uses in localize_dict.json are not broadened automatically."
    ),
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


def _upsert(items: list[Any], record: dict[str, Any]) -> None:
    record_id = str(record["id"])
    for index, item in enumerate(items):
        if isinstance(item, dict) and str(item.get("id") or "") == record_id:
            merged = dict(item)
            merged.update(record)
            items[index] = merged
            return
    items.append(dict(record))


def harden(repo_root: Path = ROOT) -> bool:
    path = repo_root / "glossary" / "ui_community_terms.json"
    payload = _load(path, {"schema_version": 1, "terms": []})
    before = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    _upsert(payload.setdefault("terms", []), UMAMUSUME_SHORTHAND_SCHEDULEBOOK)
    if before == json.dumps(payload, ensure_ascii=False, sort_keys=True):
        return False
    _write(path, payload)
    return True


def main() -> int:
    changed = harden(ROOT)
    print(f"umamusume_shorthand_schedulebook_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

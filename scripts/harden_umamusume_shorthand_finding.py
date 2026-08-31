from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

UMAMUSUME_SHORTHAND_TEXT130 = {
    "id": "world.umamusume.shorthand.text130",
    "category": "world",
    "source_aliases": ["马娘"],
    "preferred": "Mã Nương",
    "compact": [],
    "accepted": ["Mã Nương"],
    "forbidden": ["Uma Musume"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [["130"]],
    "match_mode": "contains",
    "basis": "Generic zh-CN shorthand 马娘 refers to the same world/species concept as 赛马娘 in this text-data category. Reuse the repository's established Vietnamese world term Mã Nương, but keep the rule category-scoped so unrelated proper-name or source-bridge uses elsewhere are not broadened automatically.",
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
    _upsert(payload.setdefault("terms", []), UMAMUSUME_SHORTHAND_TEXT130)
    if before == json.dumps(payload, ensure_ascii=False, sort_keys=True):
        return False
    _write(path, payload)
    return True


def main() -> int:
    changed = harden(ROOT)
    print(f"umamusume_shorthand_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

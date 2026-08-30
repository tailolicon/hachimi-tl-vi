from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ROOM_MATCH = {
    "id": "mode.room_match",
    "category": "system_label",
    "source_aliases": ["房间竞赛"],
    "preferred": "Room Match",
    "compact": [],
    "accepted": ["Room Match"],
    "forbidden": ["Đua phòng"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["localize_dict.json"],
    "key_exact": ["RoomMatch0001"],
    "match_mode": "contains",
    "basis": "Established player-facing mode name. Keep the canonical rule narrowly scoped to the proven RoomMatch0001 label while related Room Match UI is audited independently.",
}


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def harden(repo_root: Path = ROOT) -> bool:
    path = repo_root / "glossary" / "ui_community_terms.json"
    payload = _load(path)
    terms = payload.setdefault("terms", [])
    if not isinstance(terms, list):
        raise ValueError("glossary/ui_community_terms.json terms must be a list")
    before = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    for index, item in enumerate(terms):
        if isinstance(item, dict) and item.get("id") == ROOM_MATCH["id"]:
            merged = dict(item)
            merged.update(ROOM_MATCH)
            terms[index] = merged
            break
    else:
        terms.append(dict(ROOM_MATCH))
    changed = before != json.dumps(payload, ensure_ascii=False, sort_keys=True)
    if changed:
        _write(path, payload)
    return changed


def main() -> int:
    changed = harden(ROOT)
    print(f"room_match_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

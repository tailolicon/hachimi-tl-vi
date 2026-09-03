from __future__ import annotations

"""Resolve the category-144 马娘 shorthand finding without globalizing the short alias."""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TERM_ID = "common.world.umamusume.profile_shorthand"
SOURCE_ZH = "马娘"
PREFERRED = "Mã Nương"
TERM = {
    "id": TERM_ID,
    "category": "world_term",
    "source_aliases": [SOURCE_ZH],
    "preferred": PREFERRED,
    "accepted": [PREFERRED],
    "forbidden": ["Uma Musume"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [["144"]],
    "match_mode": "contains",
    "basis": "Category 144 contains character-profile taglines that use 马娘 inside generic 赛马娘 species references. Resolve the worker-reported short-token finding to the project world term Mã Nương without making 马娘 a global alias.",
}


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def harden(repo_root: Path = ROOT) -> bool:
    path = repo_root / "glossary" / "ui_community_terms.json"
    payload = _load(path)
    terms = payload.get("terms", [])
    if not isinstance(terms, list):
        raise ValueError("glossary/ui_community_terms.json terms must be a list")
    before = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    for index, item in enumerate(terms):
        if isinstance(item, dict) and str(item.get("id") or "") == TERM_ID:
            merged = dict(item)
            merged.update(TERM)
            terms[index] = merged
            break
    else:
        terms.append(dict(TERM))
    changed = before != json.dumps(payload, ensure_ascii=False, sort_keys=True)
    if changed:
        _write(path, payload)
    return changed


def main() -> int:
    changed = harden(ROOT)
    print(f"umamusume_shorthand_profile_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

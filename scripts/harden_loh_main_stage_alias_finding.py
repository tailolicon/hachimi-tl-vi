from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BASE_TERM_ID = "event.loh.main_stage"
BRIDGE_TERM_ID = "event.loh.main_stage.main_segment_alias"
ALIAS = "主赛段"

BRIDGE_TERM = {
    "id": BRIDGE_TERM_ID,
    "category": "stage",
    "source_aliases": [ALIAS],
    "preferred": "Main Stage",
    "compact": [],
    "accepted": ["Main Stage"],
    "forbidden": ["Giai đoạn chính"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["localize_dict.json"],
    "match_mode": "contains",
    "basis": "League of Heroes zh-CN alias 主赛段 names the Main Stage. Keep the existing Heroes-key rule unchanged and bridge this worker-reported alias only within localize_dict.json so unrelated prose cannot inherit the event-stage meaning.",
}


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def harden(repo_root: Path = ROOT) -> bool:
    path = repo_root / "glossary" / "ui_community_terms.json"
    payload = _load(path)
    terms = payload.get("terms")
    if not isinstance(terms, list):
        raise ValueError("glossary/ui_community_terms.json terms must be a list")

    if not any(isinstance(item, dict) and item.get("id") == BASE_TERM_ID for item in terms):
        raise ValueError(f"missing canonical base term {BASE_TERM_ID}")

    for index, item in enumerate(terms):
        if not isinstance(item, dict) or item.get("id") != BRIDGE_TERM_ID:
            continue
        merged = dict(item)
        merged.update(BRIDGE_TERM)
        if merged == item:
            return False
        terms[index] = merged
        break
    else:
        terms.append(dict(BRIDGE_TERM))

    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return True


def main() -> int:
    changed = harden(ROOT)
    print(f"loh_main_stage_alias_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

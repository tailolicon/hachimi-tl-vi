from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TERM_ID = "event.loh.main_stage"
ALIAS = "主赛段"


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

    for item in terms:
        if not isinstance(item, dict) or item.get("id") != TERM_ID:
            continue
        aliases = item.setdefault("source_aliases", [])
        if not isinstance(aliases, list):
            raise ValueError(f"{TERM_ID}.source_aliases must be a list")
        if ALIAS in aliases:
            return False
        aliases.append(ALIAS)
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        return True

    raise ValueError(f"missing canonical term {TERM_ID}")


def main() -> int:
    changed = harden(ROOT)
    print(f"loh_main_stage_alias_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

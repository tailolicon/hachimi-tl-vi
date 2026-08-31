from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ALIASES = {
    "common.style.front_runner": "领放",
    "common.style.late_surger": "居中",
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
    terms = payload.get("terms", [])
    if not isinstance(terms, list):
        raise ValueError("glossary/ui_community_terms.json terms must be a list")

    before = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    found: set[str] = set()
    for term in terms:
        if not isinstance(term, dict):
            continue
        term_id = str(term.get("id") or "")
        alias = ALIASES.get(term_id)
        if alias is None:
            continue
        found.add(term_id)
        source_aliases = [str(value) for value in term.get("source_aliases", []) if str(value)]
        term["source_aliases"] = list(dict.fromkeys([*source_aliases, alias]))

    missing = sorted(set(ALIASES) - found)
    if missing:
        raise ValueError(f"missing canonical running-style terms: {', '.join(missing)}")

    changed = before != json.dumps(payload, ensure_ascii=False, sort_keys=True)
    if changed:
        _write(path, payload)
    return changed


def main() -> int:
    changed = harden(ROOT)
    print(f"running_style_sequence_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

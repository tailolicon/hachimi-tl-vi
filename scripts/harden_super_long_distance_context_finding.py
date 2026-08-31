from __future__ import annotations

"""Guard the generic Long distance alias from firing inside 超长距离 compounds."""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TERM_ID = "common.distance.long"
EXCLUSION = "超长距离"


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
    matched = False
    for term in terms:
        if not isinstance(term, dict) or term.get("id") != TERM_ID:
            continue
        matched = True
        exclusions = [str(value) for value in term.get("exclude_source_contains", []) if str(value)]
        term["exclude_source_contains"] = list(dict.fromkeys([*exclusions, EXCLUSION]))
        term["basis"] = (
            "Common EN-version Long distance class. The zh-CN alias 长距离 must not fire as a substring "
            "inside the distinct 超长距离 compound used by super-long-distance Skill labels."
        )
        break

    if not matched:
        raise ValueError(f"missing canonical community term {TERM_ID}")

    changed = before != json.dumps(payload, ensure_ascii=False, sort_keys=True)
    if changed:
        _write(path, payload)
    return changed


def main() -> int:
    changed = harden(ROOT)
    print(f"super_long_distance_context_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

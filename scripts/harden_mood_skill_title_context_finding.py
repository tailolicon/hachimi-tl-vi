from __future__ import annotations

"""Prevent generic Mood aliases from matching the distinct 干劲十足 Skill title."""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
COMMUNITY_TERM_ID = "common.state.mood"
BRIDGE_TERM_ID = "state.mood"
EXCLUSION = "干劲十足"


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


def _add_exclusion(path: Path, term_id: str, basis: str) -> bool:
    payload = _load(path)
    terms = payload.get("terms", [])
    if not isinstance(terms, list):
        raise ValueError(f"{path} terms must be a list")

    before = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    matched = False
    for term in terms:
        if not isinstance(term, dict) or str(term.get("id") or "") != term_id:
            continue
        matched = True
        exclusions = [str(value) for value in term.get("exclude_source_contains", []) if str(value)]
        term["exclude_source_contains"] = list(dict.fromkeys([*exclusions, EXCLUSION]))
        term["basis"] = basis
        break
    if not matched:
        raise ValueError(f"missing canonical term {term_id} in {path}")

    changed = before != json.dumps(payload, ensure_ascii=False, sort_keys=True)
    if changed:
        _write(path, payload)
    return changed


def harden(repo_root: Path = ROOT) -> bool:
    community_changed = _add_exclusion(
        repo_root / "glossary" / "ui_community_terms.json",
        COMMUNITY_TERM_ID,
        "Mood is the generic player-facing やる気 / 干劲 state. The exact zh-CN Skill title 干劲十足 (JP 意気込み十分) is a distinct Skill identity and must not inherit the generic Mood matcher by substring.",
    )
    bridge_changed = _add_exclusion(
        repo_root / "glossary" / "source_bridge_terms.json",
        BRIDGE_TERM_ID,
        "干劲 is the zh-CN bridge for the generic Mood state, but the exact Skill title 干劲十足 corresponds to JP 意気込み十分 and must not be normalized to Mood by substring matching.",
    )
    return community_changed or bridge_changed


def main() -> int:
    changed = harden(ROOT)
    print(f"mood_skill_title_context_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

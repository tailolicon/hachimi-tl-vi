from __future__ import annotations

"""Prevent the generic 赛马娘 world term from rewriting the Mecha scenario proper name."""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TERM_ID = "common.world.umamusume"
# Keep the exclusion as narrow as the evidence-bearing proper-name compound.
# Excluding bare 机械赛马娘 would incorrectly suppress legitimate generic prose
# such as 机械赛马娘详情, where 赛马娘 still denotes the Mã Nương world/species term.
EXCLUSION = "机械赛马娘第三阶段"


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
    matched = False
    for term in terms:
        if not isinstance(term, dict) or term.get("id") != TERM_ID:
            continue
        matched = True
        exclusions = [str(value) for value in term.get("exclude_source_contains", []) if str(value)]
        # Remove the obsolete broad exclusion if a failed/partial earlier run
        # already persisted it, then install only the evidence-scoped compound.
        exclusions = [value for value in exclusions if value != "机械赛马娘"]
        term["exclude_source_contains"] = list(dict.fromkeys([*exclusions, EXCLUSION]))
        term["basis"] = (
            "Generic 赛马娘 remains the project world/species term Mã Nương. Only the evidence-bearing "
            "Run! Mecha Umamusume stage-3 proper-name compound 机械赛马娘第三阶段 is excluded from that generic matcher."
        )
        break
    if not matched:
        raise ValueError(f"missing canonical community term {TERM_ID}")
    changed = before != json.dumps(payload, ensure_ascii=False, sort_keys=True)
    if changed:
        _write(path, payload)
    return changed


def main() -> int:
    print(f"mecha_umamusume_context_hardening_changed={str(harden(ROOT)).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

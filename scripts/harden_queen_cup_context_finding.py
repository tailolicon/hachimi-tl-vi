from __future__ import annotations

"""Prevent Queen Cup's short zh-CN alias from overmatching TCK Jo-o Hai."""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TERM_ID = "reviewed.race_name.b4e4d79a5f98"
EXCLUSION = "TCK女王杯"


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def harden(repo_root: Path = ROOT) -> bool:
    path = repo_root / "glossary" / "term_registry.json"
    payload = _load(path)
    terms = payload.get("terms", [])
    if not isinstance(terms, list):
        raise ValueError("glossary/term_registry.json terms must be a list")

    before = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    matched = False
    for term in terms:
        if not isinstance(term, dict) or str(term.get("id") or "") != TERM_ID:
            continue
        matched = True
        exclusions = [str(value) for value in term.get("exclude_source_contains", []) if str(value)]
        term["exclude_source_contains"] = list(dict.fromkeys([*exclusions, EXCLUSION]))
        prior_note = str(term.get("note") or "").strip()
        guard_note = (
            "Context guard: the short Queen Cup alias 女王杯 must not match inside the distinct full race "
            "TCK女王杯 / TCK Jo-o Hai."
        )
        term["note"] = f"{prior_note} {guard_note}".strip() if guard_note not in prior_note else prior_note
        break

    if not matched:
        raise ValueError(f"missing canonical locked term {TERM_ID}")

    changed = before != json.dumps(payload, ensure_ascii=False, sort_keys=True)
    if changed:
        _write(path, payload)
    return changed


def main() -> int:
    print(f"queen_cup_context_hardening_changed={str(harden(ROOT)).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

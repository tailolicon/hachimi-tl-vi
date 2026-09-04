from __future__ import annotations

"""Prevent the standard-distance Skill locks from overmatching non-standard titles."""

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FINDING_ID = "cf-8faece2c0770dea4"
STANDARD_DISTANCE_IDS = {
    "reviewed.skill_name.0305d9c8ec13": "Cự ly tiêu chuẩn ×",
    "reviewed.skill_name.b10fa1bb5f44": "Cự ly tiêu chuẩn ○",
    "reviewed.skill_name.45bd6bd38cdb": "Cự ly tiêu chuẩn ◎",
}
NON_STANDARD_ALIASES = ["非根干距离×", "非根干距离○", "非根干距离◎"]
EXCLUSION_NOTE = (
    "The standard-distance lock must not fire inside the distinct 非根干距离 family; "
    "that paired terminology remains separately deferred until its canonical base is settled."
)


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
    path = repo_root / "glossary" / "term_registry.json"
    payload = _load(path)
    terms = payload.get("terms", [])
    if not isinstance(terms, list):
        raise ValueError("glossary/term_registry.json terms must be a list")

    before = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    seen: set[str] = set()
    for term in terms:
        if not isinstance(term, dict):
            continue
        term_id = str(term.get("id") or "")
        if term_id not in STANDARD_DISTANCE_IDS:
            continue
        seen.add(term_id)
        existing = [str(value) for value in term.get("exclude_source_contains", []) if str(value)]
        term["exclude_source_contains"] = list(dict.fromkeys([*existing, *NON_STANDARD_ALIASES]))
        note = str(term.get("note") or "").strip()
        if EXCLUSION_NOTE not in note:
            term["note"] = f"{note} {EXCLUSION_NOTE}".strip()

    missing = set(STANDARD_DISTANCE_IDS) - seen
    if missing:
        raise ValueError(f"missing standard-distance registry terms: {sorted(missing)}")

    changed = before != json.dumps(payload, ensure_ascii=False, sort_keys=True)
    if changed:
        _write(path, payload)
    return changed


def main() -> int:
    changed = harden(ROOT)
    print(f"non_standard_distance_context_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

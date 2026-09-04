from __future__ import annotations

"""Prevent the Skill alias 心动 from overmatching generic prose in a song description.

The full-description exclusion is intentionally narrow: review-plan rebuilds must preserve the
Skill title in direct Skill contexts while dropping only this category-128 prose false positive.
Regenerated finding IDs for this same evidence are resolved by the same evidence-backed guard.
"""

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FINDING_ID = "cf-251ca78d8992cf8d"
TERM_ID = "reviewed.skill_name.3346bd209f49"
EXCLUSION = (
    "疾驰的一等星闪耀着，充满勇气与希望的歌曲。\\n"
    "心动的预感――那就是比赛开始的信号"
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
    matched = False
    for term in terms:
        if not isinstance(term, dict) or term.get("id") != TERM_ID:
            continue
        matched = True
        exclusions = [str(value) for value in term.get("exclude_source_contains", []) if str(value)]
        term["exclude_source_contains"] = list(dict.fromkeys([*exclusions, EXCLUSION]))
        term["context_note"] = (
            "心动 is a locked Skill title only in Skill context. Do not match it inside the "
            "category-128 song description where 心动的预感 is ordinary prose about a fluttering "
            "premonition before a race."
        )
        break

    if not matched:
        raise ValueError(f"missing canonical term {TERM_ID}")

    changed = before != json.dumps(payload, ensure_ascii=False, sort_keys=True)
    if changed:
        _write(path, payload)
    return changed


def main() -> int:
    changed = harden(ROOT)
    print(f"heart_flutter_song_description_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

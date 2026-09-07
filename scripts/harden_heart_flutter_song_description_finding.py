from __future__ import annotations

"""Prevent heart-flutter Skill aliases from overmatching non-Skill text.

The exclusions are intentionally narrow: review-plan rebuilds must preserve the direct Skill
contexts while dropping only proven false positives in unrelated player-facing text.
Regenerated finding IDs for the same evidence are resolved by the context-guard resolver.
"""

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FINDING_ID = "cf-251ca78d8992cf8d"
SUPPORT_TITLE_FINDING_ID = "cf-34bb9869a98908b7"
TERM_ID = "reviewed.skill_name.3346bd209f49"
LONG_TERM_ID = "reviewed.skill_name.8009678dbfe7"
EXCLUSION = (
    "疾驰的一等星闪耀着，充满勇气与希望的歌曲。\\n"
    "心动的预感――那就是比赛开始的信号"
)
SUPPORT_TITLE_EXCLUSION = "怦然心动的记忆♪"


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


def _add_exclusions(term: dict[str, Any], values: list[str], context_note: str) -> None:
    exclusions = [str(value) for value in term.get("exclude_source_contains", []) if str(value)]
    term["exclude_source_contains"] = list(dict.fromkeys([*exclusions, *values]))
    term["context_note"] = context_note


def harden(repo_root: Path = ROOT) -> bool:
    path = repo_root / "glossary" / "term_registry.json"
    payload = _load(path)
    terms = payload.get("terms", [])
    if not isinstance(terms, list):
        raise ValueError("glossary/term_registry.json terms must be a list")

    before = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    matched: set[str] = set()
    for term in terms:
        if not isinstance(term, dict):
            continue
        term_id = str(term.get("id") or "")
        if term_id == TERM_ID:
            matched.add(term_id)
            _add_exclusions(
                term,
                [EXCLUSION, SUPPORT_TITLE_EXCLUSION],
                "心动 is a locked Skill title only in Skill context. Do not match it inside the "
                "category-128 song description where 心动的预感 is ordinary prose, or inside the "
                "distinct category-150 support unique-effect title 怦然心动的记忆♪.",
            )
        elif term_id == LONG_TERM_ID:
            matched.add(term_id)
            _add_exclusions(
                term,
                [SUPPORT_TITLE_EXCLUSION],
                "怦然心动 is a locked Skill title (JP トキメキハート), but the longer category-150 "
                "support unique-effect title 怦然心动的记忆♪ is a distinct title and must not inherit "
                "the Skill matcher by substring.",
            )

    missing = {TERM_ID, LONG_TERM_ID} - matched
    if missing:
        raise ValueError(f"missing canonical term(s): {', '.join(sorted(missing))}")

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

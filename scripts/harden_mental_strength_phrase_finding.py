from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TERM_ID = "reviewed.context.mental_strength.text147"
POWER_TERM_ID = "common.stat.power"
TERM = {
    "id": TERM_ID,
    "category": "skill_name",
    "source_aliases": ["精神力量"],
    "preferred": "Sức mạnh tinh thần",
    "compact": [],
    "accepted": ["Sức mạnh tinh thần"],
    "forbidden": ["Power"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "match_mode": "exact",
    "basis": "Retrospective review established 精神力量 as the complete text_data phrase Sức mạnh tinh thần. Exact source matching prevents longer prose from overmatching, while source-path scope is broad enough to cover the original canonical finding and lets canonical resolution close it; this does not assert an unrelated JP/Global Skill identity.",
}


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
    power_found = False
    mental_found = False
    for index, term in enumerate(terms):
        if not isinstance(term, dict):
            continue
        if term.get("id") == POWER_TERM_ID:
            power_found = True
            exclusions = [str(value) for value in term.get("exclude_source_contains", []) if str(value)]
            term["exclude_source_contains"] = list(dict.fromkeys([*exclusions, "精神力量"]))
        if term.get("id") == TERM_ID:
            mental_found = True
            merged = dict(term)
            merged.update(TERM)
            merged.pop("json_path_prefixes", None)
            terms[index] = merged

    if not power_found:
        raise ValueError(f"missing canonical community term {POWER_TERM_ID}")
    if not mental_found:
        terms.append(dict(TERM))

    changed = before != json.dumps(payload, ensure_ascii=False, sort_keys=True)
    if changed:
        _write(path, payload)
    return changed


def main() -> int:
    changed = harden(ROOT)
    print(f"mental_strength_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

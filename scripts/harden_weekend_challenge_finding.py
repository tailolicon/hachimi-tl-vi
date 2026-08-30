from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

WEEKEND_CHALLENGE = {
    "id": "event.monthly_match.weekend_challenge",
    "category": "event",
    "source_aliases": ["周末挑战"],
    "preferred": "Weekend Challenge",
    "compact": [],
    "accepted": ["Weekend Challenge"],
    "forbidden": ["Thử thách cuối tuần"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["localize_dict.json"],
    "key_exact": ["RatingRace600015"],
    "match_mode": "contains",
    "basis": "Named Monthly Match feature label. Current English community/reference usage calls this phase Weekend Challenge; keep the rule narrowly scoped to the proven RatingRace600015 UI slot so generic weekend-challenge prose is unaffected.",
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
    terms = payload.setdefault("terms", [])
    if not isinstance(terms, list):
        raise ValueError("glossary/ui_community_terms.json terms must be a list")

    before = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    for index, item in enumerate(terms):
        if isinstance(item, dict) and item.get("id") == WEEKEND_CHALLENGE["id"]:
            merged = dict(item)
            merged.update(WEEKEND_CHALLENGE)
            terms[index] = merged
            break
    else:
        terms.append(dict(WEEKEND_CHALLENGE))

    changed = before != json.dumps(payload, ensure_ascii=False, sort_keys=True)
    if changed:
        _write(path, payload)
    return changed


def main() -> int:
    changed = harden(ROOT)
    print(f"weekend_challenge_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

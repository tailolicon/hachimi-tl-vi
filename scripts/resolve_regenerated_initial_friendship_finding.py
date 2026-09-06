from __future__ import annotations

"""Resolve regenerated Initial Friendship findings from live canonical evidence.

This resolver is intentionally rerunnable after retrospective-review merges that can
rematerialize findings with a null canonical resolution.
"""

import json
from pathlib import Path
from typing import Any

try:
    from scripts.translation_review_common import community_term_matches, load_community_terms
except ModuleNotFoundError:
    from translation_review_common import community_term_matches, load_community_terms  # type: ignore[no-redef]

ROOT = Path(__file__).resolve().parents[1]
FINDING_ID = "cf-13f41d397ec5e6ad"
TERM_ID = "support.initial_friendship.effect155"
TARGET = "Initial Friendship"
OVERMATCH_FINDING_ID = "cf-375c57aaf697bbff"
OVERMATCH_TERM_ID = "common.friendship_gauge.support_effects"
OVERMATCH_TARGET = "Friendship Gauge"


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def _matches(item: dict[str, Any], terms: list[dict[str, Any]], term_id: str) -> bool:
    return any(
        str(match.get("id") or "") == term_id
        for match in community_term_matches(
            None,
            str(item.get("source_text") or ""),
            str(item.get("current_text") or ""),
            terms,
            source_path=str(item.get("source_path") or "") or None,
            json_path=item.get("json_path") if isinstance(item.get("json_path"), list) else None,
        )
    )


def resolve(repo_root: Path = ROOT) -> bool:
    path = repo_root / "glossary" / "canonical_findings.json"
    payload = _load(path)
    terms = load_community_terms(repo_root)
    before = json.dumps(payload, ensure_ascii=False, sort_keys=True)

    for finding in payload.get("findings", []):
        if not isinstance(finding, dict) or isinstance(finding.get("canonical_resolution"), dict):
            continue
        finding_id = str(finding.get("finding_id") or "")
        evidence = [item for item in finding.get("evidence", []) if isinstance(item, dict)]
        if not evidence:
            continue

        if finding_id == FINDING_ID:
            suggested = {
                str(value).strip().casefold()
                for value in finding.get("suggested_targets_vi", [])
                if str(value).strip()
            }
            if suggested and TARGET.casefold() not in suggested:
                continue
            if not all(_matches(item, terms, TERM_ID) for item in evidence):
                continue
            finding["canonical_resolution"] = {
                "layer": "community",
                "term_id": TERM_ID,
                "target_vi": TARGET,
            }
            continue

        if finding_id == OVERMATCH_FINDING_ID:
            suggested = {
                str(value).strip().casefold()
                for value in finding.get("suggested_targets_vi", [])
                if str(value).strip()
            }
            if suggested and TARGET.casefold() not in suggested:
                continue
            # This finding reports the generic Friendship Gauge alias leaking into
            # the narrower Initial Friendship compound. Resolve it only when every
            # live evidence row is positively covered by Initial Friendship and the
            # generic Friendship Gauge matcher is absent. If either condition
            # regresses, canonical refresh leaves the finding open again.
            if not all(_matches(item, terms, TERM_ID) for item in evidence):
                continue
            if any(_matches(item, terms, OVERMATCH_TERM_ID) for item in evidence):
                continue
            finding["canonical_resolution"] = {
                "layer": "context_guard",
                "term_id": OVERMATCH_TERM_ID,
                "target_vi": OVERMATCH_TARGET,
            }

    changed = before != json.dumps(payload, ensure_ascii=False, sort_keys=True)
    if changed:
        _write(path, payload)
    return changed


def main() -> int:
    changed = resolve(ROOT)
    print(f"regenerated_initial_friendship_resolution_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

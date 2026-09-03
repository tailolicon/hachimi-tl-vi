from __future__ import annotations

"""Resolve the latest regenerated 超长距离 overmatch finding after canonical refresh."""

import json
from pathlib import Path
from typing import Any

try:
    from scripts.translation_review_common import community_term_matches, load_community_terms
except ModuleNotFoundError:
    from translation_review_common import community_term_matches, load_community_terms  # type: ignore[no-redef]

ROOT = Path(__file__).resolve().parents[1]
FINDING_ID = "cf-9f625a03a4f08c41"
TERM_ID = "common.distance.long"
TARGET = "Long"


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def resolve(repo_root: Path = ROOT) -> bool:
    path = repo_root / "glossary" / "canonical_findings.json"
    payload = _load(path)
    terms = load_community_terms(repo_root)
    before = json.dumps(payload, ensure_ascii=False, sort_keys=True)

    for finding in payload.get("findings", []):
        if not isinstance(finding, dict) or str(finding.get("finding_id") or "") != FINDING_ID:
            continue
        if isinstance(finding.get("canonical_resolution"), dict):
            continue
        evidence = [item for item in finding.get("evidence", []) if isinstance(item, dict)]
        if not evidence:
            continue
        still_overmatches = False
        for item in evidence:
            matches = community_term_matches(
                None,
                str(item.get("source_text") or ""),
                str(item.get("current_text") or ""),
                terms,
                source_path=str(item.get("source_path") or "") or None,
                json_path=item.get("json_path") if isinstance(item.get("json_path"), list) else None,
            )
            if any(str(match.get("id") or "") == TERM_ID for match in matches):
                still_overmatches = True
                break
        if still_overmatches:
            continue
        finding["canonical_resolution"] = {
            "layer": "context_guard",
            "term_id": TERM_ID,
            "target_vi": TARGET,
        }

    changed = before != json.dumps(payload, ensure_ascii=False, sort_keys=True)
    if changed:
        _write(path, payload)
    return changed


def main() -> int:
    changed = resolve(ROOT)
    print(f"regenerated_super_long_distance_resolution_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

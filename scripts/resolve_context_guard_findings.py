from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from scripts.translation_review_common import community_term_matches, load_community_terms


ROOT = Path(__file__).resolve().parents[1]
GUARDS = {
    "cf-5d23e532c5359881": {
        "term_id": "common.stat.power",
        "target_vi": "Power",
    },
}


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
        if not isinstance(finding, dict):
            continue
        guard = GUARDS.get(str(finding.get("finding_id") or ""))
        if guard is None:
            continue
        evidence = [item for item in finding.get("evidence", []) if isinstance(item, dict)]
        if not evidence:
            continue
        term_id = str(guard["term_id"])
        still_overmatches = False
        for item in evidence:
            matches = community_term_matches(
                str(item.get("json_path", [None])[-1]) if item.get("source_path") == "localize_dict.json" and item.get("json_path") else None,
                str(item.get("source_text") or ""),
                str(item.get("current_text") or ""),
                terms,
                source_path=str(item.get("source_path") or "") or None,
                json_path=item.get("json_path") if isinstance(item.get("json_path"), list) else None,
            )
            if any(str(match.get("id") or "") == term_id for match in matches):
                still_overmatches = True
                break
        if still_overmatches:
            continue
        finding["canonical_resolution"] = {
            "layer": "context_guard",
            "term_id": term_id,
            "target_vi": str(guard["target_vi"]),
        }

    changed = before != json.dumps(payload, ensure_ascii=False, sort_keys=True)
    if changed:
        _write(path, payload)
    return changed


def main() -> int:
    changed = resolve(ROOT)
    print(f"context_guard_resolutions_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

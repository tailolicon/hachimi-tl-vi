from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:
    from scripts.translation_review_common import community_term_matches, load_community_terms
except ModuleNotFoundError:
    from translation_review_common import community_term_matches, load_community_terms  # type: ignore[no-redef]

ROOT = Path(__file__).resolve().parents[1]
FINDING_ID = "cf-b17becec58edec45"
TERM_ID = "common.style"
EXPECTED_SOURCE_PATH = "text_data_dict.json"
EXPECTED_PATH_PREFIX = "163"


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
    community_terms = load_community_terms(repo_root)
    before = json.dumps(payload, ensure_ascii=False, sort_keys=True)

    for finding in payload.get("findings", []):
        if not isinstance(finding, dict) or finding.get("finding_id") != FINDING_ID:
            continue
        if isinstance(finding.get("canonical_resolution"), dict):
            break
        evidence = [item for item in finding.get("evidence", []) if isinstance(item, dict)]
        if not evidence:
            break
        if not all(
            item.get("source_path") == EXPECTED_SOURCE_PATH
            and isinstance(item.get("json_path"), list)
            and item["json_path"]
            and str(item["json_path"][0]) == EXPECTED_PATH_PREFIX
            for item in evidence
        ):
            break
        still_overmatches = False
        for item in evidence:
            matches = community_term_matches(
                None,
                str(item.get("source_text") or ""),
                str(item.get("current_text") or ""),
                community_terms,
                source_path=EXPECTED_SOURCE_PATH,
                json_path=item.get("json_path"),
            )
            if any(str(match.get("id") or "") == TERM_ID for match in matches):
                still_overmatches = True
                break
        if still_overmatches:
            break
        finding["canonical_resolution"] = {
            "layer": "context_guard",
            "term_id": TERM_ID,
            "target_vi": "Style",
        }
        break

    changed = before != json.dumps(payload, ensure_ascii=False, sort_keys=True)
    if changed:
        _write(path, payload)
    return changed


def main() -> int:
    changed = resolve(ROOT)
    print(f"running_style_narrative_resolution_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

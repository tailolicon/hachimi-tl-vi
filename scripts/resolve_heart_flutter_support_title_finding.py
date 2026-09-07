from __future__ import annotations

"""Resolve the category-150 heart-flutter support-title overmatch after hardening."""

import json
from pathlib import Path
from typing import Any

try:
    from scripts.harden_heart_flutter_song_description_finding import (
        LONG_TERM_ID,
        SUPPORT_TITLE_EXCLUSION,
        SUPPORT_TITLE_FINDING_ID,
        TERM_ID,
    )
    from scripts.translation_review_common import load_locked_terms, locked_term_matches
except ModuleNotFoundError:
    from harden_heart_flutter_song_description_finding import (  # type: ignore[no-redef]
        LONG_TERM_ID,
        SUPPORT_TITLE_EXCLUSION,
        SUPPORT_TITLE_FINDING_ID,
        TERM_ID,
    )
    from translation_review_common import load_locked_terms, locked_term_matches  # type: ignore[no-redef]


ROOT = Path(__file__).resolve().parents[1]


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
    locked_terms = load_locked_terms(repo_root)
    before = json.dumps(payload, ensure_ascii=False, sort_keys=True)

    for finding in payload.get("findings", []):
        if not isinstance(finding, dict) or str(finding.get("finding_id") or "") != SUPPORT_TITLE_FINDING_ID:
            continue
        if isinstance(finding.get("canonical_resolution"), dict):
            continue
        evidence = [item for item in finding.get("evidence", []) if isinstance(item, dict)]
        if not evidence:
            continue

        clean = True
        for item in evidence:
            source = str(item.get("source_text") or "")
            if source != SUPPORT_TITLE_EXCLUSION:
                clean = False
                break
            matches = locked_term_matches(
                source,
                str(item.get("current_text") or ""),
                locked_terms,
                source_path=str(item.get("source_path") or "") or None,
                json_path=item.get("json_path") if isinstance(item.get("json_path"), list) else None,
            )
            matched_ids = {str(match.get("id") or "") for match in matches}
            if matched_ids.intersection({TERM_ID, LONG_TERM_ID}):
                clean = False
                break

        if clean:
            finding["canonical_resolution"] = {
                "layer": "context_guard",
                "term_id": LONG_TERM_ID,
                "target_vi": "Trái tim rung động",
            }

    changed = before != json.dumps(payload, ensure_ascii=False, sort_keys=True)
    if changed:
        _write(path, payload)
    return changed


def main() -> int:
    changed = resolve(ROOT)
    print(f"heart_flutter_support_title_resolution_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

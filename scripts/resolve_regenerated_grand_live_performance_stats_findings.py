from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:
    from scripts.translation_review_common import community_term_matches, load_community_terms
except ModuleNotFoundError:
    from translation_review_common import community_term_matches, load_community_terms  # type: ignore[no-redef]

ROOT = Path(__file__).resolve().parents[1]
FINDINGS = {
    "cf-8d8198c3fdff5fe8": ("scenario.grand_live.performance.visual.text_data", "Visual"),
    "cf-d11aa54842ad46b9": ("scenario.grand_live.performance.vocal.text_data", "Vocal"),
    "cf-ddb287e019039225": ("scenario.grand_live.performance.passion.text_data", "Passion"),
}


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def resolve(repo_root: Path = ROOT) -> int:
    path = repo_root / "glossary/canonical_findings.json"
    payload = _load(path)
    terms = load_community_terms(repo_root)
    changed = 0
    for finding in payload.get("findings", []):
        if not isinstance(finding, dict):
            continue
        spec = FINDINGS.get(str(finding.get("finding_id") or ""))
        if spec is None or isinstance(finding.get("canonical_resolution"), dict):
            continue
        term_id, target = spec
        suggested = {
            str(value).strip().casefold()
            for value in finding.get("suggested_targets_vi", [])
            if str(value).strip()
        }
        if suggested and target.casefold() not in suggested:
            continue
        evidence = [item for item in finding.get("evidence", []) if isinstance(item, dict)]
        if not evidence:
            continue
        covered = all(
            any(
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
            for item in evidence
        )
        if not covered:
            continue
        finding["canonical_resolution"] = {
            "layer": "community",
            "term_id": term_id,
            "target_vi": target,
        }
        changed += 1
    if changed:
        _write(path, payload)
    return changed


def main() -> int:
    print(f"regenerated_grand_live_performance_stats_resolved={resolve(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

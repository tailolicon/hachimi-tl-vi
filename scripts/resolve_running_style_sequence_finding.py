from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FINDING_ID = "cf-6ccc81e484da5f4a"
TERM_ID = "running_style.sequence"
EXPECTED_TARGET = "Front Runner / Pace Chaser / Late Surger / End Closer"
EXPECTED_TERMS = {
    "common.style.front_runner": ("领放", "Front Runner"),
    "common.style.pace_chaser": ("先行", "Pace Chaser"),
    "common.style.late_surger": ("居中", "Late Surger"),
    "common.style.end_closer": ("追赶", "End Closer"),
}


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def _canonical_sequence_is_ready(repo_root: Path) -> bool:
    payload = _load(repo_root / "glossary" / "ui_community_terms.json")
    terms = {
        str(term.get("id") or ""): term
        for term in payload.get("terms", [])
        if isinstance(term, dict)
    }
    for term_id, (alias, preferred) in EXPECTED_TERMS.items():
        term = terms.get(term_id)
        if not isinstance(term, dict):
            return False
        aliases = {str(value) for value in term.get("source_aliases", []) if str(value)}
        accepted = {str(value) for value in term.get("accepted", []) if str(value)}
        if alias not in aliases:
            return False
        if str(term.get("preferred") or "") != preferred or preferred not in accepted:
            return False
    return True


def resolve(repo_root: Path = ROOT) -> bool:
    findings_path = repo_root / "glossary" / "canonical_findings.json"
    payload = _load(findings_path)
    before = json.dumps(payload, ensure_ascii=False, sort_keys=True)

    if not _canonical_sequence_is_ready(repo_root):
        return False

    for finding in payload.get("findings", []):
        if not isinstance(finding, dict) or finding.get("finding_id") != FINDING_ID:
            continue
        if str(finding.get("source_zh_cn") or "") != "领放][先行][居中][追赶":
            break
        if str(finding.get("match_mode") or "exact") != "contains":
            break
        if finding.get("source_paths") != ["text_data_dict.json"]:
            break
        suggested = {str(value) for value in finding.get("suggested_targets_vi", []) if str(value)}
        if EXPECTED_TARGET not in suggested:
            break
        finding["canonical_resolution"] = {
            "layer": "context_guard",
            "term_id": TERM_ID,
            "target_vi": EXPECTED_TARGET,
        }
        break

    changed = before != json.dumps(payload, ensure_ascii=False, sort_keys=True)
    if changed:
        _write(findings_path, payload)
    return changed


def main() -> int:
    changed = resolve(ROOT)
    print(f"running_style_sequence_resolution_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

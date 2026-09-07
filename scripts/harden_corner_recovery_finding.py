from __future__ import annotations

"""Keep the reviewed Corner Recovery Skill lock aligned with Skill-name canon."""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ZH = "弯道回复○"
TERM_ID = "reviewed.skill_name.ab9ceceded12"
TARGET = "Hồi Phục Khúc Cua○"
NOTE = (
    "Verified コーナー回復○ / 弯道回复○ Skill identity aligned with the current "
    "Skill-name canonical target; supersedes the older Khúc cua hồi phục○ lock."
)


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def harden(repo_root: Path = ROOT) -> bool:
    registry_path = repo_root / "glossary" / "term_registry.json"
    reviews_path = repo_root / "glossary" / "terminology_reviews.json"
    registry = _load(registry_path)
    reviews = _load(reviews_path)
    changed = False

    matched_term = False
    for term in registry.get("terms", []):
        if not isinstance(term, dict) or str(term.get("id") or "") != TERM_ID:
            continue
        matched_term = True
        if term.get("target_vi") != TARGET:
            term["target_vi"] = TARGET
            changed = True
        if term.get("note") != NOTE:
            term["note"] = NOTE
            changed = True
        break
    if not matched_term:
        raise ValueError(f"missing reviewed registry term: {TERM_ID}")

    matched_decision = False
    for decision in reviews.get("decisions", []):
        if not isinstance(decision, dict):
            continue
        same_term = str(decision.get("term_id") or "") == TERM_ID
        same_source = str(decision.get("source_zh_cn") or "").strip() == SOURCE_ZH
        if not (same_term or same_source) or str(decision.get("action") or "").lower() != "lock":
            continue
        matched_decision = True
        if decision.get("target_vi") != TARGET:
            decision["target_vi"] = TARGET
            changed = True
        if decision.get("note") != NOTE:
            decision["note"] = NOTE
            changed = True
    if not matched_decision:
        raise ValueError(f"missing reviewed lock decision for {SOURCE_ZH}")

    if changed:
        _write(registry_path, registry)
        _write(reviews_path, reviews)
    return changed


def main() -> int:
    changed = harden(ROOT)
    print(f"corner_recovery_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

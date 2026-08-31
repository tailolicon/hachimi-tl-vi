from __future__ import annotations

"""Migrate legacy Senko Skill locks to the canonical Pace Chaser label.

The zh-CN token 先行 is also the source alias for the generic Pace Chaser running
style. A small family of reviewed Skill-title locks still embedded the older
romanization ``Senko``, which makes the exact Skill lock contradict the current
player-facing running-style rule. Keep the Skill-title wording, but replace only
that embedded legacy style label.
"""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FINDING_ID = "cf-f57d921afca6a993"
COMMUNITY_TERM_ID = "common.style.pace_chaser"
SOURCE_TOKEN = "先行"
LEGACY_LABEL = "Senko"
CANONICAL_LABEL = "Pace Chaser"


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


def _strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value] if value else []
    if isinstance(value, list):
        return [str(item) for item in value if str(item)]
    return []


def harden(repo_root: Path = ROOT) -> bool:
    community_path = repo_root / "glossary" / "ui_community_terms.json"
    community = _load(community_path)
    pace_rule = next(
        (
            term
            for term in community.get("terms", [])
            if isinstance(term, dict) and term.get("id") == COMMUNITY_TERM_ID
        ),
        None,
    )
    if not isinstance(pace_rule, dict):
        raise ValueError(f"missing canonical community term {COMMUNITY_TERM_ID}")
    if str(pace_rule.get("preferred") or "") != CANONICAL_LABEL:
        raise ValueError(f"{COMMUNITY_TERM_ID} no longer prefers {CANONICAL_LABEL!r}")
    if LEGACY_LABEL not in _strings(pace_rule.get("forbidden")):
        raise ValueError(f"{COMMUNITY_TERM_ID} no longer forbids {LEGACY_LABEL!r}")

    changed = False

    registry_path = repo_root / "glossary" / "term_registry.json"
    registry = _load(registry_path)
    registry_before = json.dumps(registry, ensure_ascii=False, sort_keys=True)
    migrated = 0
    for term in registry.get("terms", []):
        if not isinstance(term, dict) or not bool(term.get("locked")):
            continue
        aliases = _strings(term.get("zh_cn"))
        target = str(term.get("target_vi") or "")
        if not any(SOURCE_TOKEN in alias for alias in aliases):
            continue
        if LEGACY_LABEL not in target:
            continue
        term["target_vi"] = target.replace(LEGACY_LABEL, CANONICAL_LABEL)
        note = str(term.get("note") or "").strip()
        migration_note = (
            "Canonical hardening: embedded running-style label migrated from "
            "legacy Senko to player-facing Pace Chaser."
        )
        if migration_note not in note:
            term["note"] = f"{note} {migration_note}".strip()
        migrated += 1
    if migrated == 0:
        # Idempotent reruns are valid only when no conflicting lock remains.
        if any(
            isinstance(term, dict)
            and bool(term.get("locked"))
            and any(SOURCE_TOKEN in alias for alias in _strings(term.get("zh_cn")))
            and LEGACY_LABEL in str(term.get("target_vi") or "")
            for term in registry.get("terms", [])
        ):
            raise AssertionError("legacy Senko Skill lock remained after migration")
    if registry_before != json.dumps(registry, ensure_ascii=False, sort_keys=True):
        _write(registry_path, registry)
        changed = True

    findings_path = repo_root / "glossary" / "canonical_findings.json"
    findings = _load(findings_path)
    findings_before = json.dumps(findings, ensure_ascii=False, sort_keys=True)
    matched_finding = False
    for finding in findings.get("findings", []):
        if not isinstance(finding, dict) or finding.get("finding_id") != FINDING_ID:
            continue
        matched_finding = True
        suggestions = _strings(finding.get("suggested_targets_vi"))
        if CANONICAL_LABEL not in suggestions:
            suggestions.append(CANONICAL_LABEL)
        finding["suggested_targets_vi"] = suggestions
        break
    if not matched_finding:
        raise ValueError(f"missing canonical finding {FINDING_ID}")
    if findings_before != json.dumps(findings, ensure_ascii=False, sort_keys=True):
        _write(findings_path, findings)
        changed = True

    return changed


def main() -> int:
    changed = harden(ROOT)
    print(f"pace_chaser_skill_lock_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

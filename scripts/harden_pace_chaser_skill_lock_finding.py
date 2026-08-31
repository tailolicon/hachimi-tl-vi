from __future__ import annotations

"""Migrate legacy Senko Skill locks to the canonical Pace Chaser label.

The zh-CN token 先行 is also the source alias for the generic Pace Chaser running
style. A small family of reviewed Skill-title locks still embedded the older
romanization ``Senko``, which makes the exact Skill lock contradict the current
player-facing running-style rule. Keep the Skill-title wording, but replace only
that embedded legacy style label.

Both the reviewed decision source and its generated locked registry entry are
migrated. This is required because ``apply_terminology_reviews.py`` runs before
the normal finding-hardener sweep during context Sync; leaving the source review
on Senko would make every later Sync reject the already-hardened registry.
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
MIGRATION_NOTE = (
    "Canonical hardening: embedded running-style label migrated from "
    "legacy Senko to player-facing Pace Chaser."
)


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


def _migrate_target(record: dict[str, Any], *, source_field: str) -> bool:
    source = str(record.get(source_field) or "")
    target = str(record.get("target_vi") or "")
    if SOURCE_TOKEN not in source or LEGACY_LABEL not in target:
        return False
    record["target_vi"] = target.replace(LEGACY_LABEL, CANONICAL_LABEL)
    note = str(record.get("note") or "").strip()
    if MIGRATION_NOTE not in note:
        record["note"] = f"{note} {MIGRATION_NOTE}".strip()
    return True


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

    # Migrate the authoritative reviewed decisions first. Context Sync applies
    # these decisions before the normal finding-hardener sweep.
    reviews_path = repo_root / "glossary" / "terminology_reviews.json"
    reviews = _load(reviews_path)
    reviews_before = json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    for decision in reviews.get("decisions", []):
        if not isinstance(decision, dict) or str(decision.get("action") or "") != "lock":
            continue
        _migrate_target(decision, source_field="source_zh_cn")
    if reviews_before != json.dumps(reviews, ensure_ascii=False, sort_keys=True):
        _write(reviews_path, reviews)
        changed = True

    registry_path = repo_root / "glossary" / "term_registry.json"
    registry = _load(registry_path)
    registry_before = json.dumps(registry, ensure_ascii=False, sort_keys=True)
    for term in registry.get("terms", []):
        if not isinstance(term, dict) or not bool(term.get("locked")):
            continue
        aliases = _strings(term.get("zh_cn"))
        target = str(term.get("target_vi") or "")
        if not any(SOURCE_TOKEN in alias for alias in aliases) or LEGACY_LABEL not in target:
            continue
        term["target_vi"] = target.replace(LEGACY_LABEL, CANONICAL_LABEL)
        note = str(term.get("note") or "").strip()
        if MIGRATION_NOTE not in note:
            term["note"] = f"{note} {MIGRATION_NOTE}".strip()
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

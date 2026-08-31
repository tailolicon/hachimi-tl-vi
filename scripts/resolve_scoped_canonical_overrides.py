from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from scripts.canonical_findings import (
    BLOCKING_STATUSES,
    ROOT,
    _rule_covers_finding,
    _rule_matches_finding_source,
    _strings,
    read_json,
    write_json,
)


def _is_scoped(rule: dict[str, Any]) -> bool:
    return bool(
        _strings(rule.get("key_exact"))
        or _strings(rule.get("key_prefixes"))
        or rule.get("json_path_prefixes")
    )


def resolve_scoped_canonical_overrides(repo_root: Path, ledger: dict[str, Any] | None = None) -> dict[str, Any]:
    """Resolve context-specific community rules that intentionally override a generic reviewed lock.

    A reviewed terminology lock is source-wide, while some zh-CN aliases are polysemous in
    narrowly identifiable UI categories. The normal canonical resolver correctly refuses a
    conflicting target. This pass permits the conflict only when a community rule carries an
    explicit item/category scope and that scope fully covers the worker finding. Unscoped
    community rules can never override a reviewed lock here.
    """
    if ledger is None:
        ledger = read_json(repo_root / "glossary/canonical_findings.json", {}) or {}
    result = dict(ledger) if isinstance(ledger, dict) else {"schema_version": 1, "findings": []}
    community = read_json(repo_root / "glossary/ui_community_terms.json", {}) or {}
    rules = [
        rule
        for rule in community.get("terms", []) if isinstance(community, dict)
        if isinstance(rule, dict) and _is_scoped(rule)
    ]

    for finding in result.get("findings", []) if isinstance(result.get("findings"), list) else []:
        if not isinstance(finding, dict):
            continue
        if str(finding.get("status") or "open") not in BLOCKING_STATUSES:
            continue
        if finding.get("canonical_resolution"):
            continue
        review = finding.get("review_resolution")
        if not isinstance(review, dict) or str(review.get("action") or "") != "lock":
            continue
        reviewed_target = str(review.get("target_vi") or "").strip().casefold()
        if not reviewed_target:
            continue

        for rule in rules:
            if not _rule_covers_finding(rule, finding):
                continue
            if not _rule_matches_finding_source(rule, "source_aliases", finding):
                continue
            preferred = str(rule.get("preferred") or "").strip()
            if not preferred or preferred.casefold() == reviewed_target:
                continue
            finding["canonical_resolution"] = {
                "layer": "community",
                "term_id": str(rule.get("id") or ""),
                "target_vi": preferred,
            }
            break
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve explicitly scoped community overrides of generic reviewed locks.")
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    path = repo_root / "glossary/canonical_findings.json"
    ledger = read_json(path, {"schema_version": 1, "findings": []}) or {"schema_version": 1, "findings": []}
    before = ledger
    resolved = resolve_scoped_canonical_overrides(repo_root, ledger)
    write_json(path, resolved)
    changed = sum(
        1
        for old, new in zip(before.get("findings", []), resolved.get("findings", []))
        if isinstance(old, dict) and isinstance(new, dict)
        and not old.get("canonical_resolution") and new.get("canonical_resolution")
    )
    print(f"scoped_canonical_overrides_resolved={changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

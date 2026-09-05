from __future__ import annotations

import argparse
import copy
from pathlib import Path
from typing import Any

try:
    from scripts.canonical_findings import (
        BLOCKING_STATUSES,
        ROOT,
        _rule_covers_finding,
        _rule_matches_finding_source,
        _strings,
        read_json,
        write_json,
    )
except ModuleNotFoundError:
    from canonical_findings import (  # type: ignore[no-redef]
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


def _rule_covers_all_evidence(rule: dict[str, Any], finding: dict[str, Any]) -> bool:
    """Return true only when every concrete finding report is inside the scoped rule.

    Worker findings can be semantically broader than the item that produced them. A narrow
    canonical rule must never be promoted to source-wide coverage merely to close such a
    finding. When an explicit reviewed lock already agrees with the narrow rule, however, the
    observed finding can be considered resolved if every durable evidence row is demonstrably
    inside that rule's scope. A later report outside the scope will make this predicate false on
    the next refresh/resolution pass and reopen the finding.
    """

    evidence_rows = [row for row in finding.get("evidence", []) if isinstance(row, dict)]
    if not evidence_rows:
        return False

    for evidence in evidence_rows:
        source_path = str(evidence.get("source_path") or "").strip()
        json_path = evidence.get("json_path") if isinstance(evidence.get("json_path"), list) else []
        key = str(evidence.get("key") or "").strip()
        if not key and source_path == "localize_dict.json" and json_path:
            # localize_dict entries are top-level keyed records; historic evidence rows did not
            # persist the separate item key, but their one-element JSON path is the same key.
            key = str(json_path[0])

        evidence_scope = {
            "source_paths": [source_path] if source_path else [],
            "key_exact": [key] if key else [],
            "json_path_prefixes": [[str(value) for value in json_path]] if json_path else [],
        }
        if not _rule_covers_finding(rule, evidence_scope):
            return False

        evidence_source = str(evidence.get("source_text") or finding.get("source_zh_cn") or "")
        if not _rule_matches_finding_source(
            rule,
            "source_aliases",
            {"source_zh_cn": evidence_source},
        ):
            return False

    return True


def resolve_scoped_canonical_overrides(repo_root: Path, ledger: dict[str, Any] | None = None) -> dict[str, Any]:
    """Resolve findings from explicit context-scoped community canonical rules.

    The normal resolver intentionally requires exactly one reviewed/suggested target before a
    canonical rule may resolve a finding. Some polysemous source aliases cannot safely receive
    a source-wide reviewed lock at all, but can still be canonical inside a narrow proven UI
    scope. This pass accepts only community rules with an explicit item/category scope.

    Normally the rule must fully cover the finding's declared scope. One conservative fallback
    exists for overbroad worker findings: if an explicit review lock agrees with the scoped rule
    and *every* captured evidence item is covered by that rule, the observed finding may be
    resolved without pretending the rule is source-wide. Unscoped rules are never eligible, and
    explicit defer/ignore decisions remain blocking/ignored rather than being overridden here.
    """
    if ledger is None:
        ledger = read_json(repo_root / "glossary/canonical_findings.json", {}) or {}
    result = dict(ledger) if isinstance(ledger, dict) else {"schema_version": 1, "findings": []}
    community = read_json(repo_root / "glossary/ui_community_terms.json", {}) or {}
    rules = [
        rule
        for rule in (community.get("terms", []) if isinstance(community, dict) else [])
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
        review_action = str(review.get("action") or "") if isinstance(review, dict) else ""
        if review_action in {"defer", "ignore"}:
            continue
        reviewed_target = (
            str(review.get("target_vi") or "").strip().casefold()
            if isinstance(review, dict) and review_action == "lock"
            else ""
        )

        for rule in rules:
            if not _rule_matches_finding_source(rule, "source_aliases", finding):
                continue
            preferred = str(rule.get("preferred") or "").strip()
            if not preferred:
                continue

            declared_scope_covered = _rule_covers_finding(rule, finding)
            evidence_only_covered = False
            if not declared_scope_covered:
                # Never let a narrower rule silently broaden an unreviewed or conflicting
                # finding. The fallback is valid only when the explicit reviewed target agrees
                # and every concrete report is inside the narrow rule.
                if not reviewed_target or preferred.casefold() != reviewed_target:
                    continue
                if not _rule_covers_all_evidence(rule, finding):
                    continue
                evidence_only_covered = True

            # When the declared finding scope is already covered and the review target agrees,
            # the ordinary canonical resolver owns this case. Preserve the historical scoped-
            # override behavior only for a conflicting generic review lock. The evidence-only
            # path above is the exception that closes an overbroad worker finding safely.
            if reviewed_target and preferred.casefold() == reviewed_target and not evidence_only_covered:
                continue

            finding["canonical_resolution"] = {
                "layer": "community",
                "term_id": str(rule.get("id") or ""),
                "target_vi": preferred,
            }
            break
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve canonical findings from explicitly scoped community context rules.")
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    path = repo_root / "glossary/canonical_findings.json"
    ledger = read_json(path, {"schema_version": 1, "findings": []}) or {"schema_version": 1, "findings": []}
    before = copy.deepcopy(ledger)
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

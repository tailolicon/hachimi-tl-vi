from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
from typing import Any

from hachimi_tl_vi.parallel import set_json_path, structural_qa

try:
    from scripts.canonical_findings import active_findings, finding_matches_item, merge_worker_findings, normalize_worker_finding, refresh_canonical_resolutions
except ModuleNotFoundError:
    from canonical_findings import active_findings, finding_matches_item, merge_worker_findings, normalize_worker_finding, refresh_canonical_resolutions  # type: ignore[no-redef]

try:
    from scripts.translation_review_common import (
        contains_any,
        context_snapshot_hash,
        item_scoped_policy_hash,
        get_json_path,
        load_json,
        load_source_bridge_config,
        normalize,
        source_bridge_policy_hash,
        source_bridge_risk_matches,
        source_bridge_term_matches,
        text_fingerprint,
        utc_now,
        write_json,
    )
except ModuleNotFoundError:
    from translation_review_common import (  # type: ignore[no-redef]
        contains_any,
        context_snapshot_hash,
        item_scoped_policy_hash,
        get_json_path,
        load_json,
        load_source_bridge_config,
        normalize,
        source_bridge_policy_hash,
        source_bridge_risk_matches,
        source_bridge_term_matches,
        text_fingerprint,
        utc_now,
        write_json,
    )

CURRENT_POLICY_VERSION = 3
_ALLOWED_ACTIONS = {"keep", "revise", "defer"}
_ALLOWED_CONFIDENCE = {"high", "medium", "low"}


def _load_completion(completion_path: Path) -> dict[str, Any]:
    try:
        completion = load_json(completion_path)
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid completion marker: {completion_path}") from exc
    if not isinstance(completion, dict):
        raise ValueError(f"invalid completion marker: {completion_path}")
    return completion


def _load_result(repo_root: Path, expected_result: Path, batch_id: str) -> dict[str, Any]:
    result_path = repo_root / expected_result
    try:
        result = load_json(result_path)
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{batch_id}: invalid result file: {expected_result.as_posix()}") from exc
    if not isinstance(result, dict):
        reason = "missing" if not result_path.exists() else "not a JSON object"
        raise ValueError(f"{batch_id}: result file {reason}: {expected_result.as_posix()}")
    return result


def _load_batch(repo_root: Path, plan_id: str, batch_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
    plan_path = repo_root / "work/translation_review/plans" / f"{plan_id}.json"
    plan = load_json(plan_path)
    if plan.get("plan_id") != plan_id:
        raise ValueError(f"plan_id mismatch in {plan_path}")
    meta = next((item for item in plan.get("batches", []) if item.get("batch_id") == batch_id), None)
    if meta is None:
        raise ValueError(f"batch {batch_id} is not assigned by plan {plan_id}")
    batch = load_json(repo_root / str(meta["batch_path"]))
    if batch.get("plan_id") != plan_id or batch.get("batch_id") != batch_id:
        raise ValueError(f"batch metadata mismatch for {batch_id}")
    return plan, batch


def _validate_terms(item: dict[str, Any], candidate: str, decision: dict[str, Any], errors: list[str]) -> None:
    term_sensitive = bool(item.get("locked_terms") or item.get("community_terms") or item.get("skill_name_canonical"))
    if term_sensitive:
        basis = decision.get("terminology_basis")
        if not isinstance(basis, str) or not basis.strip():
            errors.append(f"{item['uid']}: terminology_basis is required")

    for term in item.get("locked_terms", []):
        expected = str(term.get("target_vi", ""))
        if expected and not contains_any(candidate, [expected]):
            errors.append(f"{item['uid']}: locked term {term.get('id')} requires {expected!r}")

    for term in item.get("community_terms", []):
        forbidden = [str(v) for v in term.get("forbidden", []) if str(v)]
        accepted = [str(v) for v in term.get("accepted", []) if str(v)]
        if forbidden and contains_any(candidate, forbidden):
            errors.append(f"{item['uid']}: forbidden wording survives for {term.get('id')}")
        if bool(term.get("require_accepted", True)) and accepted and not contains_any(candidate, accepted):
            errors.append(f"{item['uid']}: accepted player-facing form required for {term.get('id')}")

    skill = item.get("skill_name_canonical")
    if isinstance(skill, dict):
        expected = str(skill.get("target_vi", "")).strip()
        if expected and normalize(candidate) != normalize(expected):
            errors.append(f"{item['uid']}: canonical skill title must be {expected!r}")


def _embedded_term_defer_reasons(
    item: dict[str, Any],
    candidate: str,
    decision: dict[str, Any],
) -> list[str]:
    reasons: list[str] = []
    term_sensitive = bool(item.get("locked_terms") or item.get("community_terms") or item.get("skill_name_canonical"))
    if term_sensitive:
        basis = decision.get("terminology_basis")
        if not isinstance(basis, str) or not basis.strip():
            reasons.append("missing_terminology_basis")

    for term in item.get("locked_terms", []):
        expected = str(term.get("target_vi", ""))
        if expected and not contains_any(candidate, [expected]):
            reasons.append("locked_term_mismatch")

    for term in item.get("community_terms", []):
        forbidden = [str(v) for v in term.get("forbidden", []) if str(v)]
        accepted = [str(v) for v in term.get("accepted", []) if str(v)]
        if forbidden and contains_any(candidate, forbidden):
            reasons.append("community_forbidden_wording")
        if bool(term.get("require_accepted", True)) and accepted and not contains_any(candidate, accepted):
            reasons.append("community_term_mismatch")

    skill = item.get("skill_name_canonical")
    if isinstance(skill, dict):
        expected = str(skill.get("target_vi", "")).strip()
        if expected and normalize(candidate) != normalize(expected):
            reasons.append("canonical_skill_name_mismatch")
    return list(dict.fromkeys(reasons))


def _bridge_auto_defer_reasons(
    item: dict[str, Any],
    candidate: str,
    action: str,
    confidence: str,
    bridge_term_rules: list[dict[str, Any]],
    bridge_risk_rules: list[dict[str, Any]],
) -> tuple[list[str], list[dict[str, Any]], list[dict[str, Any]]]:
    source = str(item.get("source_text", ""))
    terms = source_bridge_term_matches(
        source,
        candidate,
        bridge_term_rules,
        key=item.get("key"),
        source_path=item.get("source_path"),
        json_path=item.get("json_path"),
    )
    risks = source_bridge_risk_matches(source, bridge_risk_rules)
    reasons: list[str] = []

    if action == "keep" and confidence != "high":
        reasons.append("non_high_confidence_keep")

    if action in {"keep", "revise"}:
        if any(term.get("forbidden_present") for term in terms):
            reasons.append("source_bridge_forbidden_calque")
        if any(
            term.get("require_accepted", True)
            and term.get("accepted")
            and not term.get("accepted_present")
            for term in terms
        ):
            reasons.append("source_bridge_term_mismatch")
        if any(risk.get("mode") == "defer_until_canonical" for risk in risks):
            reasons.append("source_bridge_untrusted_source")

    return list(dict.fromkeys(reasons)), terms, risks


def _validate_result(
    completion: dict[str, Any],
    result: dict[str, Any],
    batch: dict[str, Any],
    bridge_term_rules: list[dict[str, Any]] | None = None,
    bridge_risk_rules: list[dict[str, Any]] | None = None,
    bridge_hash: str = "",
    defer_term_conflicts: bool = False,
) -> tuple[list[dict[str, Any]], list[str]]:
    bridge_term_rules = bridge_term_rules or []
    bridge_risk_rules = bridge_risk_rules or []
    errors: list[str] = []
    for field in ("plan_id", "batch_id", "claim_id", "worker_id"):
        if result.get(field) != completion.get(field):
            errors.append(f"result/completion {field} mismatch")

    assigned = {str(item["uid"]): item for item in batch.get("items", [])}
    decisions = result.get("decisions")
    if not isinstance(decisions, list):
        return [], errors + ["decisions must be a list"]

    by_uid: dict[str, dict[str, Any]] = {}
    for decision in decisions:
        uid = str(decision.get("uid", ""))
        if not uid:
            errors.append("decision missing uid")
            continue
        if uid in by_uid:
            errors.append(f"duplicate decision for {uid}")
        by_uid[uid] = decision

    if set(by_uid) != set(assigned):
        missing = sorted(set(assigned) - set(by_uid))
        extra = sorted(set(by_uid) - set(assigned))
        if missing:
            errors.append(f"missing decisions: {missing}")
        if extra:
            errors.append(f"unassigned decisions: {extra}")

    normalized: list[dict[str, Any]] = []
    for uid, item in assigned.items():
        decision = by_uid.get(uid)
        if decision is None:
            continue
        if decision.get("current_fingerprint") != item.get("current_fingerprint"):
            errors.append(f"{uid}: current_fingerprint does not match batch")

        action = str(decision.get("action", ""))
        confidence = str(decision.get("confidence", ""))
        reason = decision.get("reason")
        if action not in _ALLOWED_ACTIONS:
            errors.append(f"{uid}: invalid action {action!r}")
            continue
        if confidence not in _ALLOWED_CONFIDENCE:
            errors.append(f"{uid}: invalid confidence {confidence!r}")
        if not isinstance(reason, str) or not reason.strip():
            errors.append(f"{uid}: reason is required")
        canonical_finding = None
        if decision.get("canonical_finding") is not None:
            try:
                canonical_finding = normalize_worker_finding(decision.get("canonical_finding"), item)
            except ValueError as exc:
                errors.append(f"{uid}: {exc}")
        if action == "revise" and confidence == "low":
            if defer_term_conflicts:
                action = "defer"
            else:
                errors.append(f"{uid}: low-confidence revisions must defer")

        proposed = decision.get("proposed_text")
        candidate = str(item.get("current_text", ""))
        if action == "revise":
            if not isinstance(proposed, str) or not proposed.strip():
                errors.append(f"{uid}: revise requires proposed_text")
            else:
                candidate = proposed
        elif proposed is not None and str(decision.get("action", "")) != "revise":
            errors.append(f"{uid}: proposed_text is only allowed for revise")

        qa = structural_qa(str(item.get("source_text", "")), candidate)
        auto_defer: list[str] = []
        if action in {"keep", "revise"} and not qa["passed"]:
            auto_defer.append("structural_qa_failed")

        bridge_defer, dynamic_bridge_terms, dynamic_bridge_risks = _bridge_auto_defer_reasons(
            item,
            candidate,
            action,
            confidence,
            bridge_term_rules,
            bridge_risk_rules,
        )
        auto_defer.extend(bridge_defer)
        if defer_term_conflicts and action in {"keep", "revise"}:
            auto_defer.extend(_embedded_term_defer_reasons(item, candidate, decision))
        auto_defer = list(dict.fromkeys(auto_defer))
        normalized_action = "defer" if auto_defer and action in {"keep", "revise"} else action

        if normalized_action in {"keep", "revise"}:
            _validate_terms(item, candidate, decision, errors)

        normalized.append({
            "uid": uid,
            "action": normalized_action,
            "submitted_action": str(decision.get("action", "")),
            "confidence": confidence,
            "reason": reason,
            "proposed_text": proposed,
            "terminology_basis": decision.get("terminology_basis"),
            "speech_basis": decision.get("speech_basis"),
            "canonical_finding": canonical_finding,
            "auto_defer_reasons": auto_defer,
            "source_bridge_terms": dynamic_bridge_terms,
            "source_bridge_risks": dynamic_bridge_risks,
            "source_bridge_policy_sha256": bridge_hash if (dynamic_bridge_terms or dynamic_bridge_risks) else None,
            "item": item,
        })
    return normalized, errors


def _current_text(repo_root: Path, docs: dict[str, Any], item: dict[str, Any]) -> str | None:
    source_path = str(item["source_path"])
    if source_path not in docs:
        path = repo_root / "localized_data" / source_path
        if not path.exists():
            return None
        docs[source_path] = load_json(path)
    try:
        current = get_json_path(docs[source_path], item["json_path"])
    except (KeyError, IndexError, TypeError):
        return None
    return current if isinstance(current, str) else None


def _defer_for_open_findings(decisions: list[dict[str, Any]], findings: list[dict[str, Any]]) -> None:
    if not findings:
        return
    for decision in decisions:
        if decision.get("action") not in {"keep", "revise"}:
            continue
        item = decision["item"]
        matches = [finding for finding in findings if finding_matches_item(
            finding, key=item.get("key"), source=str(item.get("source_text", "")),
            source_path=item.get("source_path"), json_path=item.get("json_path"),
        )]
        if not matches:
            continue
        decision["action"] = "defer"
        reasons = decision.setdefault("auto_defer_reasons", [])
        if "open_canonical_finding" not in reasons:
            reasons.append("open_canonical_finding")
        decision["canonical_findings"] = [str(row.get("finding_id") or "") for row in matches]


def merge(repo_root: Path) -> dict[str, Any]:
    review_root = repo_root / "work/translation_review"
    reviewed_path = review_root / "reviewed_index.json"
    reviewed = load_json(
        reviewed_path,
        {"schema_version": 1, "policy_version": CURRENT_POLICY_VERSION, "entries": {}},
    )
    reviewed_entries = reviewed.setdefault("entries", {})
    current_context_hash = context_snapshot_hash(repo_root)
    current_item_policy_hash = item_scoped_policy_hash(repo_root)
    bridge_hash = source_bridge_policy_hash(repo_root)
    bridge_config = load_source_bridge_config(repo_root)
    bridge_term_rules = [item for item in bridge_config.get("terms", []) if isinstance(item, dict)]
    bridge_risk_rules = [item for item in bridge_config.get("untrusted_sources", []) if isinstance(item, dict)]
    docs: dict[str, Any] = {}
    dirty_docs: set[str] = set()
    findings_path = repo_root / "glossary/canonical_findings.json"
    findings_ledger = load_json(findings_path, {"schema_version": 1, "findings": []}) or {"schema_version": 1, "findings": []}
    findings_ledger = refresh_canonical_resolutions(repo_root, findings_ledger)
    runtime_findings = active_findings(findings_ledger)

    report: dict[str, Any] = {
        "schema_version": 1,
        "policy_version": CURRENT_POLICY_VERSION,
        "generated_at": utc_now(),
        "source_bridge_policy_sha256": bridge_hash,
        "merged_batches": [],
        "stale_batches": [],
        "superseded_batches": [],
        "already_merged": [],
        "counts": {"keep": 0, "revise": 0, "defer": 0},
        "revised_uids": [],
        "unresolved_defer_uids": [],
        "auto_deferred": [],
        "canonical_findings_reported": [],
    }

    completion_paths = (
        sorted((review_root / "completions").glob("*/*.json"))
        if (review_root / "completions").exists()
        else []
    )
    for completion_path in completion_paths:
        completion = _load_completion(completion_path)
        batch_id = str(completion.get("batch_id", ""))
        plan_id = str(completion.get("plan_id", ""))
        claim_id = str(completion.get("claim_id", ""))
        if not batch_id or not plan_id or not claim_id:
            raise ValueError(f"invalid completion marker: {completion_path}")

        merged_path = review_root / "merged" / f"{batch_id}.json"
        if merged_path.exists():
            report["already_merged"].append(batch_id)
            continue

        plan, batch = _load_batch(repo_root, plan_id, batch_id)
        if (
            int(plan.get("policy_version", 0)) != CURRENT_POLICY_VERSION
            or str(plan.get("context_snapshot_sha256", "")) != current_context_hash
            or str(plan.get("item_scoped_policy_sha256", "")) != current_item_policy_hash
        ):
            if int(plan.get("policy_version", 0)) != CURRENT_POLICY_VERSION:
                reason = "legacy_policy"
            elif str(plan.get("context_snapshot_sha256", "")) != current_context_hash:
                reason = "review_context_changed"
            else:
                reason = "item_scoped_policy_changed"
            write_json(merged_path, {
                "schema_version": 1,
                "status": "superseded",
                "plan_id": plan_id,
                "batch_id": batch_id,
                "claim_id": claim_id,
                "merged_at": utc_now(),
                "superseded_reason": reason,
            })
            report["superseded_batches"].append({"batch_id": batch_id, "reason": reason})
            continue

        expected_result = Path("work/translation_review/results") / batch_id / f"{claim_id}.json"
        if completion.get("result_path") != expected_result.as_posix():
            raise ValueError(f"{batch_id}: completion result_path mismatch")
        result = _load_result(repo_root, expected_result, batch_id)
        decisions, errors = _validate_result(
            completion,
            result,
            batch,
            bridge_term_rules,
            bridge_risk_rules,
            bridge_hash,
            defer_term_conflicts=True,
        )
        if errors:
            raise ValueError(f"{batch_id}: " + "; ".join(errors))

        batch_finding_reports: list[dict[str, Any]] = []
        for decision in decisions:
            finding = decision.get("canonical_finding")
            if not isinstance(finding, dict):
                continue
            item = decision["item"]
            batch_finding_reports.append({
                "finding": finding, "uid": decision["uid"], "plan_id": plan_id, "batch_id": batch_id,
                "claim_id": claim_id, "worker_id": completion.get("worker_id"), "source_path": item.get("source_path"),
                "json_path": item.get("json_path"), "source_text": item.get("source_text"), "current_text": item.get("current_text"),
                "proposed_text": decision.get("proposed_text"), "reported_at": result.get("reviewed_at") or completion.get("completed_at") or utc_now(),
            })
        if batch_finding_reports:
            findings_ledger = merge_worker_findings(findings_ledger, batch_finding_reports)
            findings_ledger = refresh_canonical_resolutions(repo_root, findings_ledger)
            runtime_findings = active_findings(findings_ledger)
            report["canonical_findings_reported"].extend(sorted({str(row["finding"].get("finding_id") or "") for row in batch_finding_reports}))
        _defer_for_open_findings(decisions, runtime_findings)

        stale: list[str] = []
        for decision in decisions:
            current = _current_text(repo_root, docs, decision["item"])
            if current is None or text_fingerprint(current) != decision["item"]["current_fingerprint"]:
                stale.append(decision["uid"])
        if stale:
            write_json(merged_path, {
                "schema_version": 1,
                "status": "stale",
                "plan_id": plan_id,
                "batch_id": batch_id,
                "claim_id": claim_id,
                "merged_at": utc_now(),
                "stale_uids": stale,
            })
            report["stale_batches"].append({"batch_id": batch_id, "uids": stale})
            continue

        counts: Counter[str] = Counter()
        auto_deferred_for_batch: list[dict[str, Any]] = []
        for decision in decisions:
            item = decision["item"]
            uid = decision["uid"]
            action = decision["action"]
            final_text = str(item["current_text"])
            if action == "revise":
                final_text = str(decision["proposed_text"])
                source_path = str(item["source_path"])
                set_json_path(docs[source_path], item["json_path"], final_text)
                dirty_docs.add(source_path)
                report["revised_uids"].append(uid)
            elif action == "defer":
                report["unresolved_defer_uids"].append(uid)

            if decision["auto_defer_reasons"]:
                auto_record = {
                    "uid": uid,
                    "submitted_action": decision["submitted_action"],
                    "reasons": decision["auto_defer_reasons"],
                }
                report["auto_deferred"].append(auto_record)
                auto_deferred_for_batch.append(auto_record)

            reviewed_entries[uid] = {
                "source_path": item["source_path"],
                "json_path": item["json_path"],
                "source_fingerprint": item["source_fingerprint"],
                "current_fingerprint": text_fingerprint(final_text),
                "text": final_text,
                "action": action,
                "submitted_action": decision["submitted_action"],
                "confidence": decision["confidence"],
                "terminology_basis": decision.get("terminology_basis"),
                "speech_basis": decision.get("speech_basis"),
                "auto_defer_reasons": decision["auto_defer_reasons"],
                "source_bridge_policy_sha256": decision.get("source_bridge_policy_sha256"),
                "context_snapshot_sha256": current_context_hash,
                "item_context_sha256": item.get("item_context_sha256"),
                "item_scoped_policy_sha256": current_item_policy_hash,
                "policy_version": int(plan["policy_version"]),
                "plan_id": plan_id,
                "batch_id": batch_id,
                "reviewed_at": utc_now(),
            }
            counts[action] += 1
            report["counts"][action] += 1

        write_json(merged_path, {
            "schema_version": 1,
            "status": "merged",
            "policy_version": int(plan["policy_version"]),
            "plan_id": plan_id,
            "batch_id": batch_id,
            "claim_id": claim_id,
            "worker_id": completion.get("worker_id"),
            "merged_at": utc_now(),
            "counts": dict(counts),
            "gate_resolved_items": counts["keep"] + counts["revise"],
            "deferred_items": counts["defer"],
            "auto_deferred": auto_deferred_for_batch,
            "source_bridge_policy_sha256": bridge_hash,
            "item_scoped_policy_sha256": current_item_policy_hash,
        })
        report["merged_batches"].append(batch_id)

    for source_path in sorted(dirty_docs):
        write_json(repo_root / "localized_data" / source_path, docs[source_path])
    findings_ledger = refresh_canonical_resolutions(repo_root, findings_ledger)
    write_json(findings_path, findings_ledger)
    write_json(reviewed_path, reviewed)
    write_json(review_root / "merge_report.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and merge retrospective translation-review results.")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    args = parser.parse_args()
    print(json.dumps(merge(args.repo_root.resolve()), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

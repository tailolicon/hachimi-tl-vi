from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
from typing import Any

from hachimi_tl_vi.parallel import structural_qa

try:
    from scripts.ui_review_common import load_json, text_fingerprint, utc_now, visual_width, write_json
except ModuleNotFoundError:
    from ui_review_common import load_json, text_fingerprint, utc_now, visual_width, write_json  # type: ignore[no-redef]

_ALLOWED_ACTIONS = {"keep", "revise", "defer"}
_ALLOWED_CONFIDENCE = {"high", "medium", "low"}
CURRENT_UI_REVIEW_POLICY_VERSION = 3
_TERM_PATHS = (
    "glossary/term_registry.json",
    "glossary/ui_community_terms.json",
    "glossary/ui_short_forms.json",
)


def terminology_snapshot_hash(repo_root: Path) -> str:
    digest = hashlib.sha256()
    for rel in _TERM_PATHS:
        path = repo_root / rel
        digest.update(rel.encode("utf-8") + b"\0")
        if path.exists():
            digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def _load_batch(repo_root: Path, plan_id: str, batch_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
    plan_path = repo_root / "work" / "ui_review" / "plans" / f"{plan_id}.json"
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


def _norm(text: str) -> str:
    return " ".join(text.casefold().split())


def _contains_any(text: str, values: list[str]) -> bool:
    normalized = _norm(text)
    return any(_norm(value) in normalized for value in values if value)


def _validate_result(
    completion: dict[str, Any], result: dict[str, Any], batch: dict[str, Any]
) -> tuple[list[dict[str, Any]], list[str]]:
    errors: list[str] = []
    for field in ("plan_id", "batch_id", "claim_id", "worker_id"):
        if result.get(field) != completion.get(field):
            errors.append(f"result/completion {field} mismatch")

    assigned = {str(item["key"]): item for item in batch.get("items", [])}
    decisions = result.get("decisions")
    if not isinstance(decisions, list):
        return [], errors + ["decisions must be a list"]

    by_key: dict[str, dict[str, Any]] = {}
    for decision in decisions:
        key = str(decision.get("key", ""))
        if not key:
            errors.append("decision missing key")
            continue
        if key in by_key:
            errors.append(f"duplicate decision for {key}")
        by_key[key] = decision

    if set(by_key) != set(assigned):
        missing = sorted(set(assigned) - set(by_key))
        extra = sorted(set(by_key) - set(assigned))
        if missing:
            errors.append(f"missing decisions: {missing}")
        if extra:
            errors.append(f"unassigned decisions: {extra}")

    normalized: list[dict[str, Any]] = []
    for key, item in assigned.items():
        decision = by_key.get(key)
        if decision is None:
            continue
        if decision.get("current_fingerprint") != item.get("current_fingerprint"):
            errors.append(f"{key}: current_fingerprint does not match batch")
        action = str(decision.get("action", ""))
        if action not in _ALLOWED_ACTIONS:
            errors.append(f"{key}: invalid action {action!r}")
            continue
        confidence = str(decision.get("confidence", ""))
        if confidence not in _ALLOWED_CONFIDENCE:
            errors.append(f"{key}: invalid confidence {confidence!r}")
        reason = decision.get("reason")
        if not isinstance(reason, str) or not reason.strip():
            errors.append(f"{key}: reason is required")
        control_type = decision.get("control_type", "unknown")
        if not isinstance(control_type, str) or not control_type.strip():
            errors.append(f"{key}: control_type must be a string")

        proposed = decision.get("proposed_text")
        candidate_text = str(item.get("current_text", ""))
        if action == "revise":
            if confidence == "low":
                errors.append(f"{key}: low-confidence revisions must defer")
            if not isinstance(proposed, str) or not proposed.strip():
                errors.append(f"{key}: revise requires proposed_text")
            else:
                candidate_text = proposed
                qa = structural_qa(str(item["source_text"]), proposed)
                if not qa["passed"]:
                    errors.append(f"{key}: structural QA failed: {', '.join(qa['errors'])}")
                proposed_width = visual_width(proposed)
                current_width = float(item.get("current_visual_width", visual_width(str(item["current_text"]))))
                source_width = float(item.get("source_visual_width", visual_width(str(item["source_text"]))))
                budget = max(5.0, source_width * 1.55 + 0.5)
                if proposed_width > max(current_width + 1.0, budget + 1.0):
                    errors.append(f"{key}: proposed revision is materially wider than both current text and UI budget")
        elif proposed is not None:
            errors.append(f"{key}: proposed_text is only allowed for revise")

        community_terms = item.get("community_terms", [])
        if community_terms and action in {"keep", "revise"}:
            terminology_basis = decision.get("terminology_basis")
            if not isinstance(terminology_basis, str) or not terminology_basis.strip():
                errors.append(f"{key}: terminology_basis is required for matched community/game terms")
            for match in community_terms:
                if not isinstance(match, dict):
                    continue
                term_id = str(match.get("id", "community-term"))
                forbidden = [str(value) for value in match.get("forbidden", [])]
                accepted = [str(value) for value in match.get("accepted", [])]
                if forbidden and _contains_any(candidate_text, forbidden):
                    errors.append(f"{key}: uses forbidden/noncanonical wording for {term_id}")
                if bool(match.get("require_accepted", True)) and accepted and not _contains_any(candidate_text, accepted):
                    errors.append(f"{key}: must preserve an accepted player-facing form for {term_id}")

        normalized.append({
            "key": key,
            "action": action,
            "proposed_text": proposed,
            "confidence": confidence,
            "reason": reason,
            "control_type": control_type,
            "terminology_basis": decision.get("terminology_basis"),
            "item": item,
        })
    return normalized, errors


def _find_override(overrides: dict[str, Any], key: str) -> dict[str, Any] | None:
    for entry in overrides.setdefault("key_overrides", []):
        if entry.get("file") == "localize_dict.json" and entry.get("path") == [key]:
            return entry
    return None


def _upsert_override(overrides: dict[str, Any], key: str, text: str, reason: str) -> None:
    entry = _find_override(overrides, key)
    if entry is not None:
        entry["text"] = text
        entry["reason"] = reason
        return
    overrides.setdefault("key_overrides", []).append(
        {"file": "localize_dict.json", "path": [key], "text": text, "reason": reason}
    )


def _is_legacy_v2_override(entry: dict[str, Any] | None) -> bool:
    return isinstance(entry, dict) and "Reviewed by UI pipeline ui-p2-" in str(entry.get("reason", ""))


def merge(repo_root: Path) -> dict[str, Any]:
    ui_root = repo_root / "work" / "ui_review"
    localized_path = repo_root / "localized_data" / "localize_dict.json"
    overrides_path = repo_root / "glossary" / "ui_overrides.json"
    reviewed_path = ui_root / "reviewed_index.json"

    localized = load_json(localized_path)
    overrides = load_json(overrides_path)
    reviewed = load_json(reviewed_path, {"schema_version": 1, "entries": {}})
    reviewed_entries = reviewed.setdefault("entries", {})
    current_terminology_hash = terminology_snapshot_hash(repo_root)

    report: dict[str, Any] = {
        "schema_version": 1,
        "policy_version": CURRENT_UI_REVIEW_POLICY_VERSION,
        "generated_at": utc_now(),
        "merged_batches": [],
        "stale_batches": [],
        "superseded_batches": [],
        "already_merged": [],
        "counts": {"keep": 0, "revise": 0, "defer": 0},
        "revised_keys": [],
    }

    completion_paths = sorted((ui_root / "completions").glob("*/*.json")) if (ui_root / "completions").exists() else []
    for completion_path in completion_paths:
        completion = load_json(completion_path)
        batch_id = str(completion.get("batch_id", ""))
        plan_id = str(completion.get("plan_id", ""))
        claim_id = str(completion.get("claim_id", ""))
        if not batch_id or not plan_id or not claim_id:
            raise ValueError(f"invalid completion marker: {completion_path}")
        merged_path = ui_root / "merged" / f"{batch_id}.json"
        if merged_path.exists():
            report["already_merged"].append(batch_id)
            continue

        plan, batch = _load_batch(repo_root, plan_id, batch_id)
        plan_policy = int(plan.get("policy_version", 0))
        stale_term_context = (
            plan_policy >= CURRENT_UI_REVIEW_POLICY_VERSION
            and str(plan.get("terminology_snapshot_sha256", "")) != current_terminology_hash
        )
        if plan_policy < CURRENT_UI_REVIEW_POLICY_VERSION or stale_term_context:
            superseded_reason = "legacy_policy" if plan_policy < CURRENT_UI_REVIEW_POLICY_VERSION else "terminology_context_changed"
            write_json(merged_path, {
                "schema_version": 1,
                "status": "superseded",
                "plan_id": plan_id,
                "batch_id": batch_id,
                "claim_id": claim_id,
                "merged_at": utc_now(),
                "superseded_by_policy_version": CURRENT_UI_REVIEW_POLICY_VERSION,
                "superseded_reason": superseded_reason,
                "note": "Completion was intentionally not applied because its UI-review policy/context is no longer authoritative.",
            })
            report["superseded_batches"].append({"batch_id": batch_id, "reason": superseded_reason})
            continue

        expected_result_rel = Path("work") / "ui_review" / "results" / batch_id / f"{claim_id}.json"
        if completion.get("result_path") != expected_result_rel.as_posix():
            raise ValueError(f"{batch_id}: completion result_path mismatch")
        result = load_json(repo_root / expected_result_rel)
        decisions, errors = _validate_result(completion, result, batch)
        if errors:
            raise ValueError(f"{batch_id}: " + "; ".join(errors))

        stale_keys = []
        for decision in decisions:
            key = decision["key"]
            current = localized.get(key)
            if not isinstance(current, str) or text_fingerprint(current) != decision["item"]["current_fingerprint"]:
                stale_keys.append(key)
        if stale_keys:
            write_json(merged_path, {
                "schema_version": 1,
                "status": "stale",
                "plan_id": plan_id,
                "batch_id": batch_id,
                "claim_id": claim_id,
                "merged_at": utc_now(),
                "stale_keys": stale_keys,
                "note": "No decisions were applied. Changed keys remain eligible for a future UI plan.",
            })
            report["stale_batches"].append({"batch_id": batch_id, "keys": stale_keys})
            continue

        batch_counts: Counter[str] = Counter()
        for decision in decisions:
            key = decision["key"]
            action = decision["action"]
            item = decision["item"]
            final_text = str(item["current_text"])
            if action == "revise":
                final_text = str(decision["proposed_text"])
                localized[key] = final_text
                _upsert_override(overrides, key, final_text, f"Reviewed by UI pipeline {batch_id}: {decision['reason']}")
                report["revised_keys"].append(key)
            elif action == "keep":
                existing = _find_override(overrides, key)
                if _is_legacy_v2_override(existing) and str(existing.get("text", "")) == final_text:
                    _upsert_override(overrides, key, final_text, f"Reconfirmed by UI pipeline {batch_id}: {decision['reason']}")

            reviewed_entries[key] = {
                "source_fingerprint": item.get("source_fingerprint"),
                "current_fingerprint": text_fingerprint(final_text),
                "text": final_text,
                "action": action,
                "confidence": decision["confidence"],
                "control_type": decision["control_type"],
                "terminology_basis": decision.get("terminology_basis"),
                "policy_version": plan_policy,
                "plan_id": plan_id,
                "batch_id": batch_id,
                "reviewed_at": utc_now(),
            }
            batch_counts[action] += 1
            report["counts"][action] += 1

        write_json(merged_path, {
            "schema_version": 1,
            "status": "merged",
            "policy_version": plan_policy,
            "plan_id": plan_id,
            "batch_id": batch_id,
            "claim_id": claim_id,
            "worker_id": completion.get("worker_id"),
            "merged_at": utc_now(),
            "counts": dict(batch_counts),
        })
        report["merged_batches"].append(batch_id)

    write_json(localized_path, localized)
    write_json(overrides_path, overrides)
    write_json(reviewed_path, reviewed)
    write_json(ui_root / "merge_report.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and merge completed UI review batches.")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    args = parser.parse_args()
    print(json.dumps(merge(args.repo_root.resolve()), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

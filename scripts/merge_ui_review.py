from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
from typing import Any

from hachimi_tl_vi.parallel import structural_qa
from ui_review_common import load_json, text_fingerprint, utc_now, visual_width, write_json

_ALLOWED_ACTIONS = {"keep", "revise", "defer"}
_ALLOWED_CONFIDENCE = {"high", "medium", "low"}


def _load_batch(repo_root: Path, plan_id: str, batch_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
    plan_path = repo_root / "work" / "ui_review" / "plans" / f"{plan_id}.json"
    plan = load_json(plan_path)
    if plan.get("plan_id") != plan_id:
        raise ValueError(f"plan_id mismatch in {plan_path}")
    batch_meta = next((item for item in plan.get("batches", []) if item.get("batch_id") == batch_id), None)
    if batch_meta is None:
        raise ValueError(f"batch {batch_id} is not assigned by plan {plan_id}")
    batch = load_json(repo_root / str(batch_meta["batch_path"]))
    if batch.get("plan_id") != plan_id or batch.get("batch_id") != batch_id:
        raise ValueError(f"batch metadata mismatch for {batch_id}")
    return plan, batch


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
        if action == "revise":
            if confidence == "low":
                errors.append(f"{key}: low-confidence revisions must defer")
            if not isinstance(proposed, str) or not proposed.strip():
                errors.append(f"{key}: revise requires proposed_text")
            else:
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

        normalized.append(
            {
                "key": key,
                "action": action,
                "proposed_text": proposed,
                "confidence": confidence,
                "reason": reason,
                "control_type": control_type,
                "item": item,
            }
        )
    return normalized, errors


def _upsert_override(overrides: dict[str, Any], key: str, text: str, reason: str) -> None:
    entries = overrides.setdefault("key_overrides", [])
    for entry in entries:
        if entry.get("file") == "localize_dict.json" and entry.get("path") == [key]:
            entry["text"] = text
            entry["reason"] = reason
            return
    entries.append({"file": "localize_dict.json", "path": [key], "text": text, "reason": reason})


def merge(repo_root: Path) -> dict[str, Any]:
    ui_root = repo_root / "work" / "ui_review"
    localized_path = repo_root / "localized_data" / "localize_dict.json"
    overrides_path = repo_root / "glossary" / "ui_overrides.json"
    reviewed_path = ui_root / "reviewed_index.json"

    localized = load_json(localized_path)
    overrides = load_json(overrides_path)
    reviewed = load_json(reviewed_path, {"schema_version": 1, "entries": {}})
    reviewed_entries = reviewed.setdefault("entries", {})

    report: dict[str, Any] = {
        "schema_version": 1,
        "generated_at": utc_now(),
        "merged_batches": [],
        "stale_batches": [],
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

        _, batch = _load_batch(repo_root, plan_id, batch_id)
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
            write_json(
                merged_path,
                {
                    "schema_version": 1,
                    "status": "stale",
                    "plan_id": plan_id,
                    "batch_id": batch_id,
                    "claim_id": claim_id,
                    "merged_at": utc_now(),
                    "stale_keys": stale_keys,
                    "note": "No decisions were applied. Changed keys remain eligible for a future UI plan.",
                },
            )
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
                _upsert_override(
                    overrides,
                    key,
                    final_text,
                    f"Reviewed by UI pipeline {batch_id}: {decision['reason']}",
                )
                report["revised_keys"].append(key)
            reviewed_entries[key] = {
                "source_fingerprint": item.get("source_fingerprint"),
                "current_fingerprint": text_fingerprint(final_text),
                "text": final_text,
                "action": action,
                "confidence": decision["confidence"],
                "control_type": decision["control_type"],
                "plan_id": plan_id,
                "batch_id": batch_id,
                "reviewed_at": utc_now(),
            }
            batch_counts[action] += 1
            report["counts"][action] += 1

        write_json(
            merged_path,
            {
                "schema_version": 1,
                "status": "merged",
                "plan_id": plan_id,
                "batch_id": batch_id,
                "claim_id": claim_id,
                "worker_id": completion.get("worker_id"),
                "merged_at": utc_now(),
                "counts": dict(batch_counts),
            },
        )
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
    report = merge(args.repo_root.resolve())
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any

try:
    from scripts.translation_review_common import (
        canonical_finding_matches,
        community_term_matches,
        context_snapshot_hash,
        get_json_path,
        item_scoped_context_hash,
        item_scoped_policy_hash,
        load_canonical_findings,
        load_community_terms,
        load_json,
        load_locked_terms,
        load_skill_examples,
        load_source_bridge_config,
        locked_term_matches,
        risk_metadata,
        source_bridge_policy_hash,
        source_bridge_risk_matches,
        source_bridge_term_matches,
        suppress_overridden_locked_terms,
        text_fingerprint,
        utc_now,
        write_json,
    )
except ModuleNotFoundError:
    from translation_review_common import (  # type: ignore[no-redef]
        canonical_finding_matches,
        community_term_matches,
        context_snapshot_hash,
        get_json_path,
        item_scoped_context_hash,
        item_scoped_policy_hash,
        load_canonical_findings,
        load_community_terms,
        load_json,
        load_locked_terms,
        load_skill_examples,
        load_source_bridge_config,
        locked_term_matches,
        risk_metadata,
        source_bridge_policy_hash,
        source_bridge_risk_matches,
        source_bridge_term_matches,
        suppress_overridden_locked_terms,
        text_fingerprint,
        utc_now,
        write_json,
    )

TRANSLATION_REVIEW_POLICY_VERSION = 3
PRIORITY_HEAD_SIZE = 64
INCOMPLETE_GATE_REASON = "Retrospective translation review is incomplete; review continues in parallel with new translation claims."
REVIEW_WORKER_CAP = 2

# Batches containing deterministic canonical/terminology violations should not be
# buried behind merely heuristic high-risk prose. This affects only ordering of
# future regenerated plans; it never edits an active/generated plan in place.
HARD_PRIORITY_FLAGS = frozenset({
    "locked_term_mismatch",
    "community_calque_risk",
    "community_term_mismatch",
    "canonical_skill_name_mismatch",
    "source_bridge_calque_risk",
    "source_bridge_term_mismatch",
})


def _hard_violation_count(items: list[dict[str, Any]]) -> int:
    return sum(
        1
        for item in items
        if HARD_PRIORITY_FLAGS.intersection(str(flag) for flag in item.get("risk_flags", []))
    )


def _batch_priority_key(item: dict[str, Any]) -> tuple[int, int, int, str]:
    return (
        -int(item.get("hard_violation_count", 0)),
        int(item["source_batches"][0]),
        -int(item["risk_score"]),
        str(item["batch_id"]),
    )


def git_show_json(repo_root: Path, ref: str, path: str) -> Any:
    proc = subprocess.run(
        ["git", "-C", str(repo_root), "show", f"{ref}:{path}"],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return json.loads(proc.stdout)


def _load_document(repo_root: Path, cache: dict[str, Any], source_path: str) -> Any:
    if source_path not in cache:
        cache[source_path] = load_json(repo_root / "localized_data" / source_path)
    return cache[source_path]


def _compact_batch_ranges(values: list[int]) -> list[list[int]]:
    numbers = sorted({int(value) for value in values})
    if not numbers:
        return []
    ranges: list[list[int]] = []
    start = previous = numbers[0]
    for number in numbers[1:]:
        if number == previous + 1:
            previous = number
            continue
        ranges.append([start, previous])
        start = previous = number
    ranges.append([start, previous])
    return ranges


def _expand_batch_ranges(raw: Any) -> set[int]:
    result: set[int] = set()
    if not isinstance(raw, list):
        return result
    for item in raw:
        if not isinstance(item, list) or len(item) != 2:
            continue
        start, end = int(item[0]), int(item[1])
        if start <= end:
            result.update(range(start, end + 1))
    return result


def _freeze_review_scope(repo_root: Path, gate: dict[str, Any], *, reset: bool = False) -> None:
    if not reset and "review_scope_batch_ranges" in gate and "review_scope_entries" in gate:
        return
    progress = load_json(repo_root / "work/translation_progress.json", {})
    batches = [int(value) for value in progress.get("translated_batches", [])]
    gate["review_scope_batch_ranges"] = _compact_batch_ranges(batches)
    gate["review_scope_entries"] = int(progress.get("translated_entries", 0))
    gate["review_scope_frozen_at"] = utc_now()


def _set_gate(
    repo_root: Path,
    *,
    enabled: bool,
    plan_id: str | None,
    candidate_count: int,
    reason: str,
) -> None:
    path = repo_root / "work/parallel_state.json"
    state = load_json(path, {})
    gate = state.setdefault("translation_review_gate", {})
    previous_enabled = bool(gate.get("enabled"))
    if enabled:
        _freeze_review_scope(repo_root, gate, reset=not previous_enabled)
    gate.update({
        "enabled": enabled,
        "policy_version": TRANSLATION_REVIEW_POLICY_VERSION,
        "claims_allowed": True,
        "concurrent_translation_enabled": bool(enabled),
        "review_worker_cap": REVIEW_WORKER_CAP if enabled else 0,
        "active_plan_id": plan_id,
        "unresolved_entries": candidate_count,
        "protocol": "TRANSLATION_REVIEW.md",
        "reason": reason,
        "updated_at": utc_now(),
    })
    if enabled and not previous_enabled:
        gate["activated_at"] = utc_now()
    if not enabled:
        gate["cleared_at"] = utc_now()
    write_json(path, state)


def normalize_gate_state_for_noop(after: dict[str, Any], before: dict[str, Any]) -> dict[str, Any]:
    """Restore only gate timestamps when the semantic gate state is unchanged.

    Production Sync captures ``before`` prior to rebuilding. A rediscovered active
    plan may refresh ``updated_at`` even though plan identity, scope, reason, and
    policy are identical. This helper makes that unchanged second sync byte-stable
    without hiding any semantic gate change.
    """
    result = json.loads(json.dumps(after))
    old_gate = before.get("translation_review_gate") if isinstance(before, dict) else None
    new_gate = result.get("translation_review_gate") if isinstance(result, dict) else None
    if not isinstance(old_gate, dict) or not isinstance(new_gate, dict):
        return result
    volatile = {"updated_at", "activated_at", "cleared_at"}
    old_semantic = {key: value for key, value in old_gate.items() if key not in volatile}
    new_semantic = {key: value for key, value in new_gate.items() if key not in volatile}
    if old_semantic != new_semantic:
        return result
    for key in volatile:
        if key in old_gate:
            new_gate[key] = old_gate[key]
        else:
            new_gate.pop(key, None)
    return result


def _active_incomplete(repo_root: Path, context_hash: str, bridge_hash: str, item_policy_hash: str) -> dict[str, Any] | None:
    active_path = repo_root / "work/translation_review/active_plan.json"
    if not active_path.exists():
        return None
    active = load_json(active_path, {})
    if active.get("status") != "active":
        return None
    if int(active.get("policy_version", 0)) != TRANSLATION_REVIEW_POLICY_VERSION:
        return None
    if str(active.get("context_snapshot_sha256", "")) != context_hash:
        return None
    if str(active.get("source_bridge_policy_sha256", "")) != bridge_hash:
        return None
    if str(active.get("item_scoped_policy_sha256", "")) != item_policy_hash:
        return None
    plan_path = active.get("plan_path")
    if not plan_path:
        return None
    plan = load_json(repo_root / str(plan_path), {})
    unresolved = [
        batch for batch in plan.get("batches", [])
        if not (repo_root / "work/translation_review/merged" / f"{batch['batch_id']}.json").exists()
    ]
    if unresolved:
        return active
    return None


def _merged_markers(repo_root: Path) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    merged_root = repo_root / "work/merged"
    if not merged_root.exists():
        return result
    for path in sorted(merged_root.glob("batch-*.json")):
        marker = load_json(path, {})
        if marker.get("status") != "merged":
            continue
        if not marker.get("source_batch_ref"):
            continue
        result.append(marker)
    return result


def _review_scope_markers(repo_root: Path) -> list[dict[str, Any]]:
    state = load_json(repo_root / "work/parallel_state.json", {})
    gate = state.get("translation_review_gate", {}) if isinstance(state, dict) else {}
    allowed = _expand_batch_ranges(gate.get("review_scope_batch_ranges"))
    markers = _merged_markers(repo_root)
    if not allowed:
        return markers
    return [marker for marker in markers if int(marker.get("batch", 0)) in allowed]


def _prior_is_resolved(
    prior: Any,
    *,
    context_hash: str,
    source_fp: str,
    current_fp: str,
    bridge_sensitive: bool,
    bridge_hash: str,
    item_context_hash: str | None = None,
) -> bool:
    if not isinstance(prior, dict):
        return False
    if int(prior.get("policy_version", 0)) != TRANSLATION_REVIEW_POLICY_VERSION:
        return False
    if prior.get("context_snapshot_sha256") != context_hash:
        return False
    if prior.get("source_fingerprint") != source_fp or prior.get("current_fingerprint") != current_fp:
        return False
    action = str(prior.get("action", ""))
    if action not in {"keep", "revise"}:
        return False
    if action == "keep" and prior.get("confidence") != "high":
        return False
    if bridge_sensitive and prior.get("source_bridge_policy_sha256") != bridge_hash:
        return False
    prior_item_context = prior.get("item_context_sha256")
    if (prior_item_context is not None or item_context_hash is not None) and prior_item_context != item_context_hash:
        return False
    return True


def build_plan(repo_root: Path, batch_size: int) -> dict[str, Any]:
    review_root = repo_root / "work/translation_review"
    context_hash = context_snapshot_hash(repo_root)
    bridge_hash = source_bridge_policy_hash(repo_root)
    item_policy_hash = item_scoped_policy_hash(repo_root)
    active = _active_incomplete(repo_root, context_hash, bridge_hash, item_policy_hash)
    if active is not None:
        _set_gate(
            repo_root,
            enabled=True,
            plan_id=str(active.get("plan_id")),
            candidate_count=int(active.get("candidate_count", 0)),
            reason=INCOMPLETE_GATE_REASON,
        )
        return {
            "status": "active_plan_incomplete",
            "changed": False,
            "plan_id": active.get("plan_id"),
            "candidate_count": active.get("candidate_count", 0),
            "source_bridge_policy_sha256": bridge_hash,
            "item_scoped_policy_sha256": item_policy_hash,
        }

    reviewed = load_json(
        review_root / "reviewed_index.json",
        {"schema_version": 1, "policy_version": TRANSLATION_REVIEW_POLICY_VERSION, "entries": {}},
    )
    reviewed_entries = reviewed.setdefault("entries", {})
    locked_terms = load_locked_terms(repo_root)
    community_terms = load_community_terms(repo_root)
    canonical_findings = load_canonical_findings(repo_root)
    skill_examples = load_skill_examples(repo_root)
    bridge_config = load_source_bridge_config(repo_root)
    bridge_term_rules = [item for item in bridge_config.get("terms", []) if isinstance(item, dict)]
    bridge_risk_rules = [item for item in bridge_config.get("untrusted_sources", []) if isinstance(item, dict)]
    documents: dict[str, Any] = {}
    candidates: list[dict[str, Any]] = []
    merged_markers = _review_scope_markers(repo_root)
    source_commits: set[str] = set()

    for marker in merged_markers:
        batch_number = int(marker["batch"])
        source_ref = str(marker["source_batch_ref"])
        source_path = f"work/source_batches/batch-{batch_number:05d}.json"
        source_batch = git_show_json(repo_root, source_ref, source_path)
        source_commits.add(str(source_batch.get("source_commit", marker.get("source_commit", ""))))
        for entry_index, entry in enumerate(source_batch.get("entries", [])):
            if not isinstance(entry, dict):
                continue
            source_file = str(entry.get("source_path", ""))
            json_path = entry.get("json_path")
            if not source_file or not isinstance(json_path, list):
                continue
            try:
                current = get_json_path(_load_document(repo_root, documents, source_file), json_path)
            except (KeyError, IndexError, TypeError):
                continue
            if not isinstance(current, str):
                continue

            uid = str(entry.get("uid", ""))
            source = str(entry.get("source_text", ""))
            source_fp = str(entry.get("source_fingerprint", ""))
            current_fp = text_fingerprint(current)
            key = str(json_path[0]) if source_file == "localize_dict.json" and len(json_path) == 1 else None
            community = community_term_matches(
                key, source, current, community_terms, source_path=source_file, json_path=json_path
            )
            locked = locked_term_matches(
                source, current, locked_terms, key=key, source_path=source_file, json_path=json_path
            )
            locked = suppress_overridden_locked_terms(locked, community)
            skill = skill_examples.get(source)
            bridge_terms = source_bridge_term_matches(
                source, current, bridge_term_rules, key=key, source_path=source_file, json_path=json_path
            )
            bridge_risks = source_bridge_risk_matches(source, bridge_risk_rules)
            finding_matches = canonical_finding_matches(
                key, source, canonical_findings, source_path=source_file, json_path=json_path
            )
            bridge_sensitive = bool(bridge_terms or bridge_risks)
            item_context_hash = item_scoped_context_hash(
                key=key,
                source=source,
                source_path=source_file,
                json_path=json_path,
                locked_terms=locked_terms,
                community_terms=community_terms,
                canonical_findings=finding_matches,
            )

            prior = reviewed_entries.get(uid)
            if _prior_is_resolved(
                prior,
                context_hash=context_hash,
                source_fp=source_fp,
                current_fp=current_fp,
                bridge_sensitive=bridge_sensitive,
                bridge_hash=bridge_hash,
                item_context_hash=item_context_hash,
            ):
                continue

            flags, score = risk_metadata(
                source,
                current,
                locked,
                community,
                skill,
                bridge_terms,
                bridge_risks,
            )
            if finding_matches:
                flags = list(dict.fromkeys([*flags, "canonical_finding"]))
                score += 40
            candidates.append({
                "uid": uid,
                "source_batch": batch_number,
                "entry_index": entry_index,
                "kind": entry.get("kind"),
                "source_path": source_file,
                "json_path": json_path,
                "key": key,
                "source_text": source,
                "source_fingerprint": source_fp,
                "current_text": current,
                "current_fingerprint": current_fp,
                "risk_flags": flags,
                "risk_score": score,
                "locked_terms": locked,
                "community_terms": community,
                "skill_name_canonical": skill,
                "source_bridge_terms": bridge_terms,
                "source_bridge_risks": bridge_risks,
                "source_bridge_policy_sha256": bridge_hash if bridge_sensitive else None,
                "canonical_findings": finding_matches,
                "item_context_sha256": item_context_hash,
            })

    candidates.sort(key=lambda item: (int(item["source_batch"]), int(item["entry_index"]), str(item["uid"])))
    scope_digest = hashlib.sha256()
    for item in candidates:
        scope_digest.update(str(item["uid"]).encode("utf-8") + b"\0")
        scope_digest.update(str(item["source_fingerprint"]).encode("utf-8") + b"\0")
        scope_digest.update(str(item["current_fingerprint"]).encode("utf-8") + b"\0")
        # Plan identity must change when item-scoped canonical context changes.
        # Otherwise a fully merged `defer` plan can rebuild to the same batch IDs,
        # leaving authoritative merged markers permanently blocking re-review even
        # after the canonical blocker has been resolved.
        scope_digest.update(str(item.get("item_context_sha256", "")).encode("utf-8") + b"\0")
    scope_hash = scope_digest.hexdigest()
    source_label = sorted(source_commits)[0] if len(source_commits) == 1 else "multi-source"
    plan_id = (
        f"tr-p{TRANSLATION_REVIEW_POLICY_VERSION}-"
        f"{source_label[:12]}-{scope_hash[:12]}-{context_hash[:10]}-{item_policy_hash[:10]}"
    )

    active_path = review_root / "active_plan.json"
    if not candidates:
        payload = {
            "schema_version": 1,
            "status": "idle",
            "policy_version": TRANSLATION_REVIEW_POLICY_VERSION,
            "plan_id": None,
            "plan_path": None,
            "generated_at": utc_now(),
            "context_snapshot_sha256": context_hash,
            "source_bridge_policy_sha256": bridge_hash,
            "item_scoped_policy_sha256": item_policy_hash,
            "candidate_count": 0,
            "reviewed_scope": "frozen Audit Round 1 baseline from translation_review_gate.review_scope_batch_ranges",
            "note": "All entries in the frozen Audit Round 1 baseline are resolved under the current translation-review policy/context.",
        }
        write_json(active_path, payload)
        _set_gate(
            repo_root,
            enabled=False,
            plan_id=None,
            candidate_count=0,
            reason="All currently merged translations passed retrospective review.",
        )
        return {"status": "idle", "changed": True, "candidate_count": 0}

    batch_dir = review_root / "batches" / plan_id
    if batch_dir.exists():
        for old in batch_dir.glob("*.json"):
            old.unlink()

    batches: list[dict[str, Any]] = []
    for offset in range(0, len(candidates), batch_size):
        index = offset // batch_size + 1
        batch_id = f"{plan_id}-b{index:04d}"
        items = candidates[offset:offset + batch_size]
        rel = Path("work/translation_review/batches") / plan_id / f"{batch_id}.json"
        write_json(repo_root / rel, {
            "schema_version": 1,
            "policy_version": TRANSLATION_REVIEW_POLICY_VERSION,
            "plan_id": plan_id,
            "batch_id": batch_id,
            "context_snapshot_sha256": context_hash,
            "source_bridge_policy_sha256": bridge_hash,
            "review_generation": "retrospective-canonical-full-review",
            "context_mode": "embedded-first-lazy-extra",
            "items": items,
        })
        batches.append({
            "batch_id": batch_id,
            "batch_path": rel.as_posix(),
            "item_count": len(items),
            "risk_score": sum(int(item["risk_score"]) for item in items),
            "hard_violation_count": _hard_violation_count(items),
            "source_batches": sorted({int(item["source_batch"]) for item in items}),
        })

    batches.sort(key=_batch_priority_key)
    priority_batch_ids = [str(item["batch_id"]) for item in batches[:PRIORITY_HEAD_SIZE]]
    plan_rel = Path("work/translation_review/plans") / f"{plan_id}.json"
    common = {
        "schema_version": 1,
        "policy_version": TRANSLATION_REVIEW_POLICY_VERSION,
        "plan_id": plan_id,
        "generated_at": utc_now(),
        "lease_minutes": 45,
        "context_snapshot_sha256": context_hash,
        "source_bridge_policy_sha256": bridge_hash,
        "item_scoped_policy_sha256": item_policy_hash,
        "scope_snapshot_sha256": scope_hash,
        "candidate_count": len(candidates),
        "batch_count": len(batches),
        "canonical_merged_batch_count": len(merged_markers),
        "review_generation": "retrospective-canonical-full-review",
        "worker_context_mode": "embedded-first-lazy-extra",
    }
    write_json(repo_root / plan_rel, {
        **common,
        "batch_size": batch_size,
        "supersedes_policy_versions": [1, 2],
        "batches": batches,
        "decision_actions": ["keep", "revise", "defer"],
        "protocol": "TRANSLATION_REVIEW.md",
        "defer_policy": "defer remains unresolved in the audit gate; it does not globally freeze the separate new-translation lane",
        "source_bridge_policy": "Manual bridge terms plus generated curation-backed lossy-source risks are enforced item-by-item; unresolved lossy bridge sources defer until canonicalized.",
    })
    write_json(active_path, {
        **common,
        "status": "active",
        "plan_path": plan_rel.as_posix(),
        "batch_size": batch_size,
        "batch_path_pattern": f"work/translation_review/batches/{plan_id}/{plan_id}-b{{index:04d}}.json",
        "priority_batch_ids": priority_batch_ids,
        "priority_head_size": len(priority_batch_ids),
        "worker_note": "Normal workers do not need to read plan_path; use priority_batch_ids then hashed numeric fallback. source_bridge_terms/source_bridge_risks embedded in an item are mandatory review context.",
    })
    _set_gate(
        repo_root,
        enabled=True,
        plan_id=plan_id,
        candidate_count=len(candidates),
        reason=INCOMPLETE_GATE_REASON,
    )
    return {
        "status": "active",
        "changed": True,
        "policy_version": TRANSLATION_REVIEW_POLICY_VERSION,
        "plan_id": plan_id,
        "candidate_count": len(candidates),
        "batch_count": len(batches),
        "canonical_merged_batch_count": len(merged_markers),
        "priority_head_size": len(priority_batch_ids),
        "context_snapshot_sha256": context_hash,
        "source_bridge_policy_sha256": bridge_hash,
        "item_scoped_policy_sha256": item_policy_hash,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a full retrospective review plan for already merged translations.")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--batch-size", type=int, default=20)
    args = parser.parse_args()
    if not 1 <= args.batch_size <= 100:
        raise SystemExit("--batch-size must be between 1 and 100")
    print(json.dumps(build_plan(args.repo_root.resolve(), args.batch_size), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

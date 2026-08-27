from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any

try:
    from scripts.translation_review_common import (
        community_term_matches,
        context_snapshot_hash,
        get_json_path,
        load_community_terms,
        load_json,
        load_locked_terms,
        load_skill_examples,
        locked_term_matches,
        risk_metadata,
        suppress_overridden_locked_terms,
        text_fingerprint,
        utc_now,
        write_json,
    )
except ModuleNotFoundError:
    from translation_review_common import (  # type: ignore[no-redef]
        community_term_matches,
        context_snapshot_hash,
        get_json_path,
        load_community_terms,
        load_json,
        load_locked_terms,
        load_skill_examples,
        locked_term_matches,
        risk_metadata,
        suppress_overridden_locked_terms,
        text_fingerprint,
        utc_now,
        write_json,
    )

TRANSLATION_REVIEW_POLICY_VERSION = 2


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
    gate.update({
        "enabled": enabled,
        "policy_version": TRANSLATION_REVIEW_POLICY_VERSION,
        "claims_allowed": not enabled,
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


def _active_incomplete(repo_root: Path, context_hash: str) -> dict[str, Any] | None:
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


def build_plan(repo_root: Path, batch_size: int) -> dict[str, Any]:
    review_root = repo_root / "work/translation_review"
    context_hash = context_snapshot_hash(repo_root)
    active = _active_incomplete(repo_root, context_hash)
    if active is not None:
        _set_gate(
            repo_root,
            enabled=True,
            plan_id=str(active.get("plan_id")),
            candidate_count=int(active.get("candidate_count", 0)),
            reason="Retrospective translation review is incomplete; new translation claims are paused.",
        )
        return {
            "status": "active_plan_incomplete",
            "changed": False,
            "plan_id": active.get("plan_id"),
            "candidate_count": active.get("candidate_count", 0),
        }

    reviewed = load_json(
        review_root / "reviewed_index.json",
        {"schema_version": 1, "policy_version": TRANSLATION_REVIEW_POLICY_VERSION, "entries": {}},
    )
    reviewed_entries = reviewed.setdefault("entries", {})
    locked_terms = load_locked_terms(repo_root)
    community_terms = load_community_terms(repo_root)
    skill_examples = load_skill_examples(repo_root)
    documents: dict[str, Any] = {}
    candidates: list[dict[str, Any]] = []
    merged_markers = _merged_markers(repo_root)
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
            prior = reviewed_entries.get(uid)
            if (
                isinstance(prior, dict)
                and int(prior.get("policy_version", 0)) == TRANSLATION_REVIEW_POLICY_VERSION
                and prior.get("context_snapshot_sha256") == context_hash
                and prior.get("source_fingerprint") == source_fp
                and prior.get("current_fingerprint") == current_fp
                and prior.get("action") in {"keep", "revise"}
            ):
                continue

            key = str(json_path[0]) if source_file == "localize_dict.json" and len(json_path) == 1 else None
            community = community_term_matches(key, source, current, community_terms)
            locked = locked_term_matches(source, current, locked_terms)
            locked = suppress_overridden_locked_terms(locked, community)
            skill = skill_examples.get(source)
            flags, score = risk_metadata(source, current, locked, community, skill)
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
            })

    candidates.sort(key=lambda item: (int(item["source_batch"]), int(item["entry_index"]), str(item["uid"])))
    scope_digest = hashlib.sha256()
    for item in candidates:
        scope_digest.update(str(item["uid"]).encode("utf-8") + b"\0")
        scope_digest.update(str(item["source_fingerprint"]).encode("utf-8") + b"\0")
        scope_digest.update(str(item["current_fingerprint"]).encode("utf-8") + b"\0")
    scope_hash = scope_digest.hexdigest()
    source_label = sorted(source_commits)[0] if len(source_commits) == 1 else "multi-source"
    plan_id = (
        f"tr-p{TRANSLATION_REVIEW_POLICY_VERSION}-"
        f"{source_label[:12]}-{scope_hash[:12]}-{context_hash[:10]}"
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
            "candidate_count": 0,
            "reviewed_scope": "all canonical entries represented by work/merged markers",
            "note": "All currently merged translations are resolved under the current translation-review policy/context.",
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
            "review_generation": "retrospective-canonical-full-review",
            "items": items,
        })
        batches.append({
            "batch_id": batch_id,
            "batch_path": rel.as_posix(),
            "item_count": len(items),
            "risk_score": sum(int(item["risk_score"]) for item in items),
            "source_batches": sorted({int(item["source_batch"]) for item in items}),
        })

    batches.sort(key=lambda item: (-int(item["risk_score"]), int(item["source_batches"][0]), str(item["batch_id"])))
    plan_rel = Path("work/translation_review/plans") / f"{plan_id}.json"
    common = {
        "schema_version": 1,
        "policy_version": TRANSLATION_REVIEW_POLICY_VERSION,
        "plan_id": plan_id,
        "generated_at": utc_now(),
        "lease_minutes": 45,
        "context_snapshot_sha256": context_hash,
        "scope_snapshot_sha256": scope_hash,
        "candidate_count": len(candidates),
        "batch_count": len(batches),
        "canonical_merged_batch_count": len(merged_markers),
        "review_generation": "retrospective-canonical-full-review",
    }
    write_json(repo_root / plan_rel, {
        **common,
        "batch_size": batch_size,
        "supersedes_policy_versions": [1],
        "batches": batches,
        "decision_actions": ["keep", "revise", "defer"],
        "protocol": "TRANSLATION_REVIEW.md",
        "defer_policy": "defer remains unresolved and keeps the translation gate closed",
    })
    write_json(active_path, {**common, "status": "active", "plan_path": plan_rel.as_posix()})
    _set_gate(
        repo_root,
        enabled=True,
        plan_id=plan_id,
        candidate_count=len(candidates),
        reason="Review every already merged translation before accepting new translation claims.",
    )
    return {
        "status": "active",
        "changed": True,
        "policy_version": TRANSLATION_REVIEW_POLICY_VERSION,
        "plan_id": plan_id,
        "candidate_count": len(candidates),
        "batch_count": len(batches),
        "canonical_merged_batch_count": len(merged_markers),
        "context_snapshot_sha256": context_hash,
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

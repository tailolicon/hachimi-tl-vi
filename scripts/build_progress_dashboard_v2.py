#!/usr/bin/env python3
from __future__ import annotations

import math
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import build_progress_dashboard as legacy


_BATCH_RE = re.compile(r"batch-(\d+)$")
_TASK_RE = re.compile(r"batch-(\d+)-s(\d+)$")


def _load(path: Path, default=None):
    return legacy.load(path, {} if default is None else default)


def _batch_entry_count(batch: int, queued: int, batch_size: int, total_batches: int) -> int:
    if batch < 1 or batch > total_batches or batch_size <= 0:
        return 0
    if batch < total_batches:
        return batch_size
    return max(0, queued - batch_size * (total_batches - 1)) or batch_size


def _legacy_merged(root: Path, source_commit: str) -> dict[int, int]:
    out: dict[int, int] = {}
    merged_root = root / "work/merged"
    if not merged_root.exists():
        return out
    for path in merged_root.glob("batch-*.json"):
        marker = _load(path)
        if source_commit and marker.get("source_commit") not in (None, source_commit):
            continue
        if marker.get("status") not in (None, "merged"):
            continue
        try:
            batch = int(marker.get("batch"))
            count = int(marker.get("entry_count"))
        except (TypeError, ValueError):
            continue
        if batch > 0 and count > 0:
            out[batch] = count
    return out


def _legacy_completed(root: Path, source_commit: str) -> set[int]:
    found: set[int] = set()
    completion_root = root / "work/completions"
    if not completion_root.exists():
        return found
    for batch_dir in completion_root.iterdir():
        if not batch_dir.is_dir():
            continue
        match = _BATCH_RE.fullmatch(batch_dir.name)
        if not match:
            continue
        batch = int(match.group(1))
        for path in batch_dir.glob("*.json"):
            marker = _load(path)
            if source_commit and marker.get("source_commit") not in (None, source_commit):
                continue
            if marker.get("status") not in (None, "ready_to_merge", "complete", "completed"):
                continue
            found.add(batch)
            break
    return found


def _parallel_markers(root: Path, kind: str, source_commit: str) -> dict[tuple[int, int], int]:
    found: dict[tuple[int, int], int] = {}
    parallel_root = root / "work/parallel"
    if not parallel_root.exists():
        return found
    for epoch_dir in parallel_root.iterdir():
        if not epoch_dir.is_dir():
            continue
        epoch = _load(epoch_dir / "epoch.json")
        if source_commit and epoch.get("source_commit") != source_commit:
            continue
        task_size = int(epoch.get("task_size") or 20)
        marker_root = epoch_dir / kind
        if not marker_root.exists():
            continue
        for path in marker_root.rglob("*.json"):
            marker = _load(path)
            if source_commit and marker.get("source_commit") not in (None, source_commit):
                continue
            task_id = str(marker.get("task_id") or path.stem)
            match = _TASK_RE.fullmatch(task_id)
            if not match:
                continue
            batch, shard = int(match.group(1)), int(match.group(2))
            try:
                count = int(marker.get("entry_count") or task_size)
            except (TypeError, ValueError):
                count = task_size
            if count > 0:
                found[(batch, shard)] = count
    return found


def _fully_covered_batches(
    task_keys: set[tuple[int, int]],
    *,
    queued: int,
    batch_size: int,
    total_batches: int,
    task_size: int,
    excluded: set[int],
) -> set[int]:
    shards: dict[int, set[int]] = defaultdict(set)
    for batch, shard in task_keys:
        if batch not in excluded:
            shards[batch].add(shard)
    complete: set[int] = set()
    for batch, present in shards.items():
        count = _batch_entry_count(batch, queued, batch_size, total_batches)
        expected = math.ceil(count / task_size) if count else 0
        if expected and set(range(expected)).issubset(present):
            complete.add(batch)
    return complete


def translation(root: Path, now: datetime):
    p = _load(root / "work/translation_progress.json")
    total = int(p.get("source_total_entries") or 0)
    queued = int(p.get("queued_entries") or 0)
    deferred = int(p.get("deferred_entries") or 0)
    batches = int(p.get("queue_total_batches") or 0)
    batch_size = int(p.get("batch_size") or 80)
    source_commit = str(p.get("source_commit") or "")

    state = _load(root / "work/parallel_state.json")
    epoch_path = state.get("current_epoch_metadata")
    epoch = _load(root / str(epoch_path)) if epoch_path else {}
    task_size = int(epoch.get("task_size") or 20)

    merged = _legacy_merged(root, source_commit)
    legacy_completed = _legacy_completed(root, source_commit)
    merged_batches = set(merged)
    legacy_worker_batches = merged_batches | legacy_completed

    parallel_completed = _parallel_markers(root, "completed", source_commit)
    parallel_aggregated = _parallel_markers(root, "aggregated", source_commit)
    completed_tasks = {**parallel_completed, **parallel_aggregated}

    # A full legacy merge wins over any old/stale shard for that batch. This
    # prevents double-counting if an epoch's legacy baseline was not reconciled.
    parallel_completed = {
        key: count for key, count in completed_tasks.items() if key[0] not in merged_batches
    }
    parallel_aggregated = {
        key: count for key, count in parallel_aggregated.items() if key[0] not in merged_batches
    }

    canonical_entries = sum(merged.values()) + sum(parallel_aggregated.values())
    pending_legacy_batches = legacy_worker_batches - merged_batches
    pending_legacy_entries = sum(
        _batch_entry_count(batch, queued, batch_size, batches) for batch in pending_legacy_batches
    )
    worker_entries = (
        sum(merged.values())
        + pending_legacy_entries
        + sum(parallel_completed.values())
    )
    canonical_entries = min(queued, canonical_entries)
    worker_entries = min(queued, worker_entries)

    parallel_worker_full = _fully_covered_batches(
        set(parallel_completed), queued=queued, batch_size=batch_size,
        total_batches=batches, task_size=task_size, excluded=merged_batches,
    )
    parallel_merged_full = _fully_covered_batches(
        set(parallel_aggregated), queued=queued, batch_size=batch_size,
        total_batches=batches, task_size=task_size, excluded=merged_batches,
    )
    worker_batches = legacy_worker_batches | parallel_worker_full
    canonical_batches = merged_batches | parallel_merged_full

    warnings: list[str] = []
    metadata_done = int(p.get("translated_entries") or 0)
    if metadata_done != canonical_entries:
        warnings.append(
            f"translation_progress.translated_entries={metadata_done} differs from artifact-derived canonical_entries={canonical_entries}"
        )
    first_parallel = int(epoch.get("first_parallel_batch") or 1)
    explicit_legacy = {int(x) for x in (epoch.get("legacy_completed_batches") or [])}
    effective_epoch_legacy = set(range(1, max(first_parallel, 1))) | explicit_legacy
    if epoch and effective_epoch_legacy != merged_batches:
        missing = sorted(merged_batches - effective_epoch_legacy)
        stale = sorted(effective_epoch_legacy - merged_batches)
        warnings.append(
            "parallel epoch legacy baseline differs from work/merged"
            f" (missing={missing[:8]}, stale={stale[:8]})"
        )

    return {
        "source_total_entries": total,
        "queued_entries": queued,
        "deferred_entries": deferred,
        "translated_entries": canonical_entries,
        "worker_completed_entries": worker_entries,
        "remaining_queue_entries": max(queued - canonical_entries, 0),
        "raw_percent": legacy.percent(canonical_entries, total),
        "queue_percent": legacy.percent(canonical_entries, queued),
        "batches_total": batches,
        "batches_translated": len(canonical_batches),
        "batches_worker_completed": len(worker_batches),
        "batches_pending_merge": len(worker_batches - canonical_batches),
        "worker_percent": legacy.percent(worker_entries, queued),
        "estimated_worker_entries": worker_entries,
        "batches_reviewed": len(p.get("reviewed_batches") or []),
        "batches_qa": len(p.get("qa_passed_batches") or []),
        "claims": legacy.claims(root / "work/claims", now),
        "progress_source": "artifact_reconciliation_v2",
        "metadata_translated_entries": metadata_done,
        "legacy_merged_batches": len(merged_batches),
        "legacy_completed_unmerged_batches": len(pending_legacy_batches),
        "parallel_tasks_completed": len(parallel_completed),
        "parallel_tasks_aggregated": len(parallel_aggregated),
        "parallel_tasks_pending_merge": len(set(parallel_completed) - set(parallel_aggregated)),
        "warnings": warnings,
    }


def markdown(data):
    text = legacy.markdown(data)
    warnings = data.get("translation", {}).get("warnings") or []
    if not warnings:
        return text
    block = "\n> ⚠️ Progress reconciliation: " + " | ".join(warnings) + "\n"
    return text.replace("\n## Canonical / phát hành\n", block + "\n## Canonical / phát hành\n", 1)


legacy.translation = translation
legacy.markdown = markdown


if __name__ == "__main__":
    legacy.main()

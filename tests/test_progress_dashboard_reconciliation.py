from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from scripts.build_progress_dashboard_v2 import translation


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_translation_progress_is_derived_from_artifacts(tmp_path: Path) -> None:
    source_commit = "abc123"
    _write(tmp_path / "work/translation_progress.json", {
        "source_commit": source_commit,
        "source_total_entries": 1000,
        "queued_entries": 240,
        "deferred_entries": 760,
        "queue_total_batches": 3,
        "batch_size": 80,
        "translated_entries": 999,
        "translated_batches": [1, 2, 3],
    })
    _write(tmp_path / "work/parallel_state.json", {
        "current_epoch_metadata": "work/parallel/e1/epoch.json"
    })
    _write(tmp_path / "work/parallel/e1/epoch.json", {
        "epoch": "e1",
        "source_commit": source_commit,
        "task_size": 20,
        "legacy_completed_batches": [1],
    })

    _write(tmp_path / "work/merged/batch-00001.json", {
        "batch": 1,
        "source_commit": source_commit,
        "entry_count": 80,
        "status": "merged",
    })
    _write(tmp_path / "work/completions/batch-00002/claim.json", {
        "batch": 2,
        "source_commit": source_commit,
        "status": "ready_to_merge",
    })

    # One canonical parallel shard in batch 3 and one additional completed shard
    # waiting for aggregation. Worker progress must include both, canonical only one.
    _write(tmp_path / "work/parallel/e1/completed/b0000/batch-00003-s00.json", {
        "task_id": "batch-00003-s00",
        "source_commit": source_commit,
        "entry_count": 20,
    })
    _write(tmp_path / "work/parallel/e1/aggregated/b0000/batch-00003-s00.json", {
        "task_id": "batch-00003-s00",
        "source_commit": source_commit,
        "entry_count": 20,
    })
    _write(tmp_path / "work/parallel/e1/completed/b0000/batch-00003-s01.json", {
        "task_id": "batch-00003-s01",
        "source_commit": source_commit,
        "entry_count": 20,
    })

    state = translation(tmp_path, datetime.now(timezone.utc))

    assert state["translated_entries"] == 100  # 80 legacy + 20 aggregated
    assert state["worker_completed_entries"] == 200  # +80 legacy pending +20 pending shard
    assert state["metadata_translated_entries"] == 999
    assert state["parallel_tasks_aggregated"] == 1
    assert state["parallel_tasks_completed"] == 2
    assert state["parallel_tasks_pending_merge"] == 1
    assert state["legacy_completed_unmerged_batches"] == 1
    assert state["progress_source"] == "artifact_reconciliation_v2"
    assert state["warnings"]


def test_parallel_shards_do_not_double_count_a_legacy_merged_batch(tmp_path: Path) -> None:
    source_commit = "abc123"
    _write(tmp_path / "work/translation_progress.json", {
        "source_commit": source_commit,
        "source_total_entries": 80,
        "queued_entries": 80,
        "queue_total_batches": 1,
        "batch_size": 80,
        "translated_entries": 80,
    })
    _write(tmp_path / "work/parallel_state.json", {
        "current_epoch_metadata": "work/parallel/e1/epoch.json"
    })
    _write(tmp_path / "work/parallel/e1/epoch.json", {
        "epoch": "e1",
        "source_commit": source_commit,
        "task_size": 20,
        "legacy_completed_batches": [],
    })
    _write(tmp_path / "work/merged/batch-00001.json", {
        "batch": 1,
        "source_commit": source_commit,
        "entry_count": 80,
        "status": "merged",
    })
    _write(tmp_path / "work/parallel/e1/aggregated/b0000/batch-00001-s00.json", {
        "task_id": "batch-00001-s00",
        "source_commit": source_commit,
        "entry_count": 20,
    })

    state = translation(tmp_path, datetime.now(timezone.utc))
    assert state["translated_entries"] == 80
    assert state["parallel_tasks_aggregated"] == 0

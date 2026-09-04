from __future__ import annotations

import json
import runpy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_json(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_worker_policy_requires_progress_backed_leases() -> None:
    policy = load_json("work/worker_session_policy.json")

    assert policy["policy_version"] >= 5
    assert policy["maintenance_stages"] == [
        "domain_work",
        "ready_for_finalize",
        "finalizing",
        "complete",
    ]
    assert "progress_token" in policy["maintenance_progress_evidence_rule"]
    assert "time-only heartbeat" in policy["maintenance_heartbeat_rule"]
    assert "serialized" in policy["canonical_integration_rule"]
    assert "parallel" in policy["canonical_parallel_rule"]


def test_worker_policy_is_execution_backend_independent() -> None:
    policy = load_json("work/worker_session_policy.json")
    worker_start = (ROOT / "WORKER_START.md").read_text(encoding="utf-8")

    assert "execution-backend independent" in policy["execution_backend_rule"]
    assert "not a task-level blocker" in policy["execution_backend_rule"]
    assert "connected GitHub read/write capabilities" in policy["backend_failure_fallback_rule"]
    assert "Do not release or end a worker solely because one execution backend failed" in policy[
        "backend_failure_handoff_rule"
    ]
    assert "Execution-backend independence" in worker_start
    assert "NOT a task-level blocker" in worker_start


def test_worker_policy_requires_continuous_runtime_until_platform_cutoff() -> None:
    policy = load_json("work/worker_session_policy.json")
    worker_start = (ROOT / "WORKER_START.md").read_text(encoding="utf-8")
    worker_continuous = (ROOT / "WORKER_CONTINUOUS.md").read_text(encoding="utf-8")
    autopilot = (ROOT / "AUTOPILOT.md").read_text(encoding="utf-8")

    for key in ("session_minutes", "productive_target_minutes", "stop_new_batch_after_minutes", "handoff_start_minutes"):
        assert key not in policy
    assert "checkpoint is durability, not a stop condition" in policy["partial_checkpoint_rule"]
    assert "There is no worker session timer" in policy["runtime_rule"]
    assert "commit/push" in policy["emergency_handoff_rule"]
    assert "immediately re-read live routing" in policy["continuation_rule"]

    assert "checkpoint is not stop" in worker_start.lower()
    assert "checkpointing is not a stop condition" in worker_continuous.lower()
    assert "A completed unit is a continuation trigger" in worker_continuous
    assert "MUST NOT self-time" in autopilot


def test_parallel_protocol_separates_domain_work_from_integration() -> None:
    state = load_json("work/orchestration/state.json")
    protocol = (ROOT / state["canonical_parallel_protocol"]).read_text(encoding="utf-8")
    worker_start = (ROOT / "WORKER_START.md").read_text(encoding="utf-8")

    assert "Domain work is parallel. Integration is serial." in protocol
    assert "do not stop" in protocol
    assert "ready_for_integration" in protocol
    assert "live-main canonical integration" in protocol
    assert "Domain work is parallel; live-main integration is serial." in worker_start
    assert "do not stop and do not wait for that domain to finish" in worker_start


def test_live_orchestration_state_has_explicit_valid_stage() -> None:
    policy = load_json("work/worker_session_policy.json")
    state = load_json("work/orchestration/state.json")
    active = state["active_task"]

    assert state["schema_version"] >= 3
    assert state["orchestration_version"] >= 3

    if state["phase"] == "canonical_hardening":
        assert active["stage"] in policy["maintenance_stages"]
    else:
        assert active.get("stage")
        assert active["stage"] not in {"domain_work", "ready_for_finalize", "finalizing"}

    matches = [item for item in state["roadmap"] if item["id"] == active["task_id"]]
    assert len(matches) == 1
    assert matches[0]["status"] == active["status"]
    assert matches[0].get("stage") == active["stage"]

    if active["stage"] in {"ready_for_finalize", "finalizing"}:
        assert active.get("domain_work_summary")
        assert active.get("finalization_scope")


def test_live_primary_maintenance_claim_carries_progress_evidence() -> None:
    policy = load_json("work/worker_session_policy.json")
    state = load_json("work/orchestration/state.json")
    claim = load_json("work/orchestration/maintenance_claim.json")

    assert claim["schema_version"] >= 2
    assert claim["stage"] in policy["maintenance_stages"]
    assert claim.get("progress_token")
    assert claim.get("progress_kind")
    assert claim.get("progress_ref")
    assert claim.get("last_progress_at")

    if claim["status"] == "active":
        assert not state["terminal"]
        assert claim.get("task_id")
        if state["phase"] == "canonical_hardening":
            assert claim["task_id"] == state["active_task"]["task_id"]


def test_readme_progress_renderer_exposes_maintenance_stage() -> None:
    module = runpy.run_path(str(ROOT / "scripts/update_root_readme_progress.py"))
    build_block = module["build_block"]

    progress = {
        "translation": {},
        "translation_review": {},
        "ui_review": {},
        "curation": {},
        "workers": {},
    }
    state = {
        "phase": "canonical_hardening",
        "active_task": {
            "task_id": "canonical-training-support",
            "title": "Training Support hardening",
            "branch": "canonical-training-support-hardening",
            "stage": "ready_for_finalize",
        },
        "canonical_parallelism": {"enabled": True},
        "roadmap": [],
    }

    block = build_block(progress, state)
    assert "stage **ready_for_finalize**" in block


def test_legacy_active_task_stage_defaults_to_domain_work() -> None:
    module = runpy.run_path(str(ROOT / "scripts/update_root_readme_progress.py"))
    maintenance_stage = module["maintenance_stage"]

    assert maintenance_stage({"status": "active"}) == "domain_work"
    assert maintenance_stage({"status": "complete"}) == "complete"

from __future__ import annotations

import json
import runpy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_json(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_worker_policy_requires_progress_backed_maintenance_heartbeat() -> None:
    policy = load_json("work/worker_session_policy.json")

    assert policy["policy_version"] >= 2
    assert policy["maintenance_stages"] == [
        "domain_work",
        "ready_for_finalize",
        "finalizing",
        "complete",
    ]
    assert "progress_token" in policy["maintenance_progress_evidence_rule"]
    assert "time-only heartbeat" in policy["maintenance_heartbeat_rule"]
    assert "ready_for_finalize" in policy["maintenance_finalizer_rule"]


def test_worker_policy_is_execution_backend_independent() -> None:
    policy = load_json("work/worker_session_policy.json")
    worker_start = (ROOT / "WORKER_START.md").read_text(encoding="utf-8")

    assert policy["policy_version"] >= 3
    assert "execution-backend independent" in policy["execution_backend_rule"]
    assert "not a task-level blocker" in policy["execution_backend_rule"]
    assert "connected GitHub read/write capabilities" in policy["backend_failure_fallback_rule"]
    assert "Do not release or end a worker solely because one execution backend failed" in policy[
        "backend_failure_handoff_rule"
    ]
    assert "Execution-backend independence" in worker_start
    assert "NOT a task-level blocker" in worker_start
    assert "Do not release/checkpoint merely because one backend failed" in worker_start


def test_worker_policy_targets_full_productive_session() -> None:
    policy = load_json("work/worker_session_policy.json")
    worker_start = (ROOT / "WORKER_START.md").read_text(encoding="utf-8")
    worker_25 = (ROOT / "WORKER_25MIN.md").read_text(encoding="utf-8")
    autopilot = (ROOT / "AUTOPILOT.md").read_text(encoding="utf-8")

    assert policy["policy_version"] >= 4
    assert policy["productive_target_minutes"] == 22
    assert policy["stop_new_batch_after_minutes"] >= 21
    assert policy["handoff_start_minutes"] == 22
    assert policy["session_minutes"] == 25
    assert "checkpoint is durability, not a stop condition" in policy["partial_checkpoint_rule"]
    assert "do not voluntarily end" in policy["productive_session_rule"]
    assert "immediately re-read live routing" in policy["continuation_rule"]
    assert "same owner should atomically transition" in policy["maintenance_finalizer_rule"]

    assert "checkpoint is not stop" in worker_start.lower()
    assert "A stage boundary is a durability boundary, not a mandatory session boundary" in worker_start
    assert "continue the next immediately runnable roadmap task" in worker_start
    assert "checkpointing is not a stop condition" in worker_25
    assert "A completed unit is a continuation trigger" in worker_25
    assert "stage boundaries are durability boundaries, not mandatory worker boundaries" in autopilot
    assert "Never idle merely to reach the handoff minute" in autopilot


def test_live_orchestration_state_has_explicit_valid_stage() -> None:
    policy = load_json("work/worker_session_policy.json")
    state = load_json("work/orchestration/state.json")
    active = state["active_task"]

    assert state["schema_version"] >= 2
    assert state["orchestration_version"] >= 2
    assert active["stage"] in policy["maintenance_stages"]

    active_roadmap = [item for item in state["roadmap"] if item.get("status") == "active"]
    assert len(active_roadmap) == 1
    assert active_roadmap[0]["id"] == active["task_id"]
    assert active_roadmap[0].get("stage") == active["stage"]

    if active["stage"] in {"ready_for_finalize", "finalizing"}:
        assert active.get("domain_work_summary")
        assert active.get("finalization_scope")


def test_live_maintenance_claim_carries_progress_evidence() -> None:
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
        assert claim["task_id"] == state["active_task"]["task_id"]
        assert claim["stage"] == state["active_task"]["stage"]


def test_universal_router_has_bounded_finalizer_mode() -> None:
    worker_start = (ROOT / "WORKER_START.md").read_text(encoding="utf-8")
    autopilot = (ROOT / "AUTOPILOT.md").read_text(encoding="utf-8")

    for stage in ("domain_work", "ready_for_finalize", "finalizing", "complete"):
        assert stage in worker_start
        assert stage in autopilot

    assert "time-only heartbeat" in worker_start
    assert "must not restart broad inventory" in autopilot.lower()


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
            "task_id": "canonical-race",
            "title": "Race hardening",
            "branch": "canonical-race-hardening-20260828",
            "stage": "ready_for_finalize",
        },
    }

    block = build_block(progress, state)
    assert "stage **ready_for_finalize**" in block


def test_legacy_active_task_stage_defaults_to_domain_work() -> None:
    module = runpy.run_path(str(ROOT / "scripts/update_root_readme_progress.py"))
    maintenance_stage = module["maintenance_stage"]

    assert maintenance_stage({"status": "active"}) == "domain_work"
    assert maintenance_stage({"status": "complete"}) == "complete"

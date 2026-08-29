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

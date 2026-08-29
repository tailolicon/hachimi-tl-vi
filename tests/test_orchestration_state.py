from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "work/orchestration/state.json"


def load_state() -> dict:
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def test_universal_entrypoint_and_spawn_prompt_are_persistent() -> None:
    state = load_state()
    assert state["entrypoint"] == "WORKER_START.md"
    assert state["autopilot_protocol"] == "AUTOPILOT.md"
    assert state["canonical_parallel_protocol"] == "CANONICAL_PARALLEL.md"
    assert state["short_spawn_prompt"] == "Run tailolicon/hachimi-tl-vi/WORKER_START.md from main."
    assert (ROOT / state["entrypoint"]).is_file()
    assert (ROOT / state["autopilot_protocol"]).is_file()
    assert (ROOT / state["canonical_parallel_protocol"]).is_file()


def test_canonical_domain_work_is_parallel_but_integration_is_serial() -> None:
    state = load_state()
    assert state["schema_version"] >= 3
    assert state["orchestration_version"] >= 3

    parallel = state["canonical_parallelism"]
    assert parallel["enabled"] is True
    assert parallel["domain_work_parallel"] is True
    assert parallel["integration_serial"] is True
    assert parallel["primary_claim_path"] == "work/orchestration/maintenance_claim.json"
    assert parallel["domain_claim_dir"] == "work/orchestration/domain_claims"

    active = state["active_task"]
    assert active["primary_lane"] is True
    assert active["integration_serial"] is True
    assert active["domain_work_parallel"] is True
    assert active["blocks_mass_work"] is True


def test_parallel_canonical_tasks_have_independent_claim_files() -> None:
    state = load_state()
    roadmap = state["roadmap"]
    ids = [item["id"] for item in roadmap]
    assert len(ids) == len(set(ids))

    active = state["active_task"]
    matches = [item for item in roadmap if item["id"] == active["task_id"]]
    assert len(matches) == 1
    assert matches[0]["status"] == "active"
    assert (ROOT / active["task_file"]).is_file()

    parallel_tasks = [
        item
        for item in roadmap
        if item.get("kind") == "canonical_hardening"
        and item.get("parallel_eligible") is True
        and item["id"] != active["task_id"]
        and item.get("status") != "complete"
    ]
    assert parallel_tasks
    for item in parallel_tasks:
        claim_path = item.get("claim_path")
        assert claim_path, item["id"]
        path = ROOT / claim_path
        assert path.is_file(), item["id"]
        claim = json.loads(path.read_text(encoding="utf-8"))
        assert claim["task_id"] == item["id"]
        assert claim["branch"] == item["branch"]
        assert claim["status"] in {"unclaimed", "active", "released", "ready_for_integration", "complete"}


def test_final_conflict_sweep_is_dependency_gated_not_parallel() -> None:
    state = load_state()
    sweep = next(item for item in state["roadmap"] if item["id"] == "canonical-final-conflict-sweep")
    assert sweep["parallel_eligible"] is False
    deps = set(sweep["depends_on"])
    assert {
        "canonical-race",
        "canonical-training-support",
        "canonical-character-training-ui",
        "canonical-resources-gacha-shop",
        "canonical-missions-events",
        "canonical-common-ui-system",
    } <= deps


def test_every_roadmap_phase_has_repository_owned_instructions() -> None:
    state = load_state()
    for item in state["roadmap"]:
        task_file = item.get("task_file")
        assert task_file, item["id"]
        assert (ROOT / task_file).is_file(), item["id"]


def test_full_pinned_corpus_is_not_allowed_to_stop_at_initial_queue() -> None:
    state = load_state()
    ids = {item["id"] for item in state["roadmap"]}
    assert "translate-pinned-corpus" in ids
    assert "deferred-wave-expansion" in ids
    assert "post-completion-audit-round2" in ids
    assert "post-completion-audit-round3" in ids
    assert "final-release-verification" in ids
    assert state["completion_policy"]["source_coverage_required"] is True
    assert state["completion_policy"]["deferred_entries_must_be_zero"] is True
    assert state["completion_policy"]["minimum_post_completion_full_audit_rounds"] >= 2


def test_nonblocking_song_and_staff_scope_is_explicit() -> None:
    state = load_state()
    skipped = set(state["scope_policy"]["skip_as_blocking_domains"])
    assert {"songs", "lyrics", "staff_names", "creator_credits"} <= skipped


def test_legacy_next_session_file_redirects_to_universal_entrypoint() -> None:
    text = (ROOT / "NEXT_SESSION.md").read_text(encoding="utf-8")
    assert "WORKER_START.md" in text
    assert "Run `tailolicon/hachimi-tl-vi/WORKER_START.md` from `main`." in text

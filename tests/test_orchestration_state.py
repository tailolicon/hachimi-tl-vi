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
    assert state["short_spawn_prompt"] == "Run tailolicon/hachimi-tl-vi/WORKER_START.md from main."
    assert (ROOT / state["entrypoint"]).is_file()
    assert (ROOT / state["autopilot_protocol"]).is_file()


def test_active_task_is_unique_and_backed_by_persistent_file() -> None:
    state = load_state()
    roadmap = state["roadmap"]
    ids = [item["id"] for item in roadmap]
    assert len(ids) == len(set(ids))

    active = state["active_task"]
    matches = [item for item in roadmap if item["id"] == active["task_id"]]
    assert len(matches) == 1
    assert matches[0]["status"] == "active"
    assert Path(active["task_file"]).as_posix() == matches[0]["task_file"]
    assert (ROOT / active["task_file"]).is_file()

    if state["phase"] == "canonical_hardening":
        assert state["blocking_maintenance"] is True
        assert active["serial"] is True
        assert active["blocks_mass_work"] is True


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

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def test_shared_worker_policy_is_safe_for_25_minute_sessions() -> None:
    policy = _load("work/worker_session_policy.json")

    session = int(policy["session_minutes"])
    lease = int(policy["rolling_lease_minutes"])
    heartbeat = int(policy["heartbeat_every_minutes"])
    checkpoint = int(policy["checkpoint_every_decisions"])
    stop_new = int(policy["stop_new_batch_after_minutes"])
    handoff = int(policy["handoff_start_minutes"])

    assert session == 25
    assert 1 <= heartbeat < lease < session
    assert lease <= heartbeat * 2
    assert checkpoint == 5
    assert 0 < stop_new < handoff < session
    assert "released" in policy["claim_statuses"]
    assert "partial_result_path" in policy["released_claim_rule"]


def test_parallel_state_points_to_shared_worker_policy() -> None:
    state = _load("work/parallel_state.json")
    assert state["worker_session_policy"] == "work/worker_session_policy.json"


def test_protocols_document_partial_release_handoff() -> None:
    for rel in ("TRANSLATION_REVIEW.md", "UI_REVIEW.md", "PARALLEL_TRANSLATION.md"):
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert "worker_session_policy" in text
        assert "released" in text
        assert "partial_result_path" in text


def test_top_level_25_minute_orchestrator_prioritizes_old_audit() -> None:
    text = (ROOT / "WORKER_25MIN.md").read_text(encoding="utf-8")
    translation_audit = text.index("retrospective translation audit")
    ui_audit = text.index("retrospective UI audit")
    new_translation = text.index("new untranslated content")
    assert translation_audit < ui_audit < new_translation

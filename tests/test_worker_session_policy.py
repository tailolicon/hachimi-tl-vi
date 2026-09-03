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


def test_top_level_25_minute_orchestrator_allocates_review_and_translation_concurrently() -> None:
    text = (ROOT / "WORKER_25MIN.md").read_text(encoding="utf-8")
    assert "Retrospective translation audit remains mandatory" in text
    assert "it is no longer a global stop for new translation" in text
    assert "review_worker_cap" in text
    assert "route this worker directly to Mode C" in text
    assert "Only after the translation-review gate clears:" in text
    assert "no higher-priority required UI audit remains" in text


def test_worker_policy_prevents_exact_match_for_embedded_canonical_aliases() -> None:
    policy = _load("work/worker_session_policy.json")
    rule = policy["canonical_finding_match_rule"]
    assert "exact is valid ONLY" in rule
    assert "complete reviewed item.source_text" in rule
    assert "use match_mode=contains" in rule
    assert "may be quarantined" in rule

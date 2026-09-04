from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def test_shared_worker_policy_has_no_self_timed_session_cutoff() -> None:
    policy = _load("work/worker_session_policy.json")

    for key in (
        "session_minutes",
        "productive_target_minutes",
        "heartbeat_every_minutes",
        "stop_new_batch_after_minutes",
        "handoff_start_minutes",
    ):
        assert key not in policy

    assert int(policy["rolling_lease_minutes"]) > 0
    assert int(policy["checkpoint_every_decisions"]) == 5
    assert "There is no worker session timer" in policy["runtime_rule"]
    assert "actual platform/runtime termination signal" in policy["platform_cutoff_rule"]
    assert "commit/push" in policy["emergency_handoff_rule"]
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


def test_top_level_continuous_orchestrator_allocates_review_and_translation_concurrently() -> None:
    text = (ROOT / "WORKER_CONTINUOUS.md").read_text(encoding="utf-8")
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

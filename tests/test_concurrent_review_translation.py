from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from scripts import build_translation_review_plan as builder
from scripts.build_progress_dashboard_v3 import translation_review


def _write(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def test_active_review_gate_opens_translation_lane_and_freezes_scope(tmp_path: Path, monkeypatch) -> None:
    _write(tmp_path / "work/translation_progress.json", {
        "translated_batches": [1, 2, 4],
        "translated_entries": 240,
    })
    _write(tmp_path / "work/parallel_state.json", {
        "translation_review_gate": {"enabled": True},
    })
    for batch in (1, 2, 4, 5):
        _write(tmp_path / "work/merged" / f"batch-{batch:05d}.json", {
            "status": "merged",
            "batch": batch,
            "source_batch_ref": f"source-{batch}",
        })

    counter = iter(range(1, 20))
    monkeypatch.setattr(builder, "utc_now", lambda: f"2026-09-03T00:00:{next(counter):02d}Z")
    builder._set_gate(tmp_path, enabled=True, plan_id="plan-a", candidate_count=40, reason=builder.INCOMPLETE_GATE_REASON)

    state = json.loads((tmp_path / "work/parallel_state.json").read_text(encoding="utf-8"))
    gate = state["translation_review_gate"]
    assert gate["enabled"] is True
    assert gate["claims_allowed"] is True
    assert gate["concurrent_translation_enabled"] is True
    assert gate["review_worker_cap"] == 2
    assert gate["review_scope_batch_ranges"] == [[1, 2], [4, 4]]
    assert gate["review_scope_entries"] == 240
    frozen_at = gate["review_scope_frozen_at"]
    assert [row["batch"] for row in builder._review_scope_markers(tmp_path)] == [1, 2, 4]

    # New translation progress must not enlarge the still-active Audit Round 1 scope.
    _write(tmp_path / "work/translation_progress.json", {
        "translated_batches": [1, 2, 4, 5],
        "translated_entries": 260,
    })
    builder._set_gate(tmp_path, enabled=True, plan_id="plan-b", candidate_count=30, reason=builder.INCOMPLETE_GATE_REASON)
    gate = json.loads((tmp_path / "work/parallel_state.json").read_text(encoding="utf-8"))["translation_review_gate"]
    assert gate["review_scope_batch_ranges"] == [[1, 2], [4, 4]]
    assert gate["review_scope_entries"] == 240
    assert gate["review_scope_frozen_at"] == frozen_at
    assert [row["batch"] for row in builder._review_scope_markers(tmp_path)] == [1, 2, 4]


def test_dashboard_keeps_frozen_audit_denominator_as_translation_grows(tmp_path: Path) -> None:
    _write(tmp_path / "work/parallel_state.json", {
        "translation_review_gate": {
            "enabled": True,
            "claims_allowed": True,
            "policy_version": 3,
            "review_scope_entries": 240,
        }
    })
    _write(tmp_path / "work/translation_review/active_plan.json", {
        "status": "active",
        "policy_version": 3,
        "plan_id": "plan-a",
        "candidate_count": 40,
        "batch_count": 2,
    })
    _write(tmp_path / "work/translation_review/reviewed_index.json", {
        "entries": {
            "a": {"policy_version": 3, "action": "keep"},
            "b": {"policy_version": 3, "action": "defer"},
        }
    })

    review = translation_review(tmp_path, datetime.now(timezone.utc), canonical_entries=260)
    assert review["scope_total_entries"] == 240
    assert review["unresolved_entries"] == 40
    assert review["resolved_entries"] == 200
    assert review["claims_allowed"] is True


def test_worker_protocols_encode_dual_lane_routing() -> None:
    root = Path(__file__).resolve().parents[1]
    worker = (root / "WORKER_CONTINUOUS.md").read_text(encoding="utf-8")
    translation = (root / "PARALLEL_TRANSLATION.md").read_text(encoding="utf-8")
    review = (root / "TRANSLATION_REVIEW.md").read_text(encoding="utf-8")

    assert "review_worker_cap" in worker
    assert "route this worker directly to Mode C" in worker
    assert "If `claims_allowed == false`" in translation
    assert "translation_review_gate.enabled == true` or `claims_allowed == false" not in translation
    assert "review and new translation run concurrently" in review

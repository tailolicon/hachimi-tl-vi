from __future__ import annotations

import json
from pathlib import Path

import scripts.build_translation_review_plan as builder


def _write(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _patch_single_entry_plan(monkeypatch, *, item_contexts: list[str] | None = None) -> None:
    source_batch = {
        "source_commit": "67f8551f77807292cebd2b20b2c752b652393835",
        "entries": [{
            "uid": "zhcn:test-race-gate", "kind": "localize", "source_path": "localize_dict.json",
            "json_path": ["RaceTest"], "source_text": "比赛", "source_fingerprint": "source-fp",
        }],
    }
    monkeypatch.setattr(builder, "git_show_json", lambda *_args, **_kwargs: source_batch)
    monkeypatch.setattr(builder, "context_snapshot_hash", lambda _root: "context-hash")
    monkeypatch.setattr(builder, "source_bridge_policy_hash", lambda _root: "bridge-hash")
    monkeypatch.setattr(builder, "item_scoped_policy_hash", lambda _root: "item-policy-hash")
    monkeypatch.setattr(builder, "load_locked_terms", lambda _root: [])
    monkeypatch.setattr(builder, "load_community_terms", lambda _root: [])
    monkeypatch.setattr(builder, "load_canonical_findings", lambda _root: [])
    monkeypatch.setattr(builder, "load_skill_examples", lambda _root: {})
    monkeypatch.setattr(builder, "load_source_bridge_config", lambda _root: {"terms": [], "untrusted_sources": []})
    if item_contexts is not None:
        contexts = iter(item_contexts)
        monkeypatch.setattr(builder, "item_scoped_context_hash", lambda **_kwargs: next(contexts))


def test_fresh_plan_then_unchanged_rebuild_is_timestamp_only_and_normalizes_to_noop(tmp_path: Path, monkeypatch) -> None:
    _write(tmp_path / "localized_data/localize_dict.json", {"RaceTest": "Cuộc đua"})
    _write(tmp_path / "work/parallel_state.json", {"translation_review_gate": {"enabled": False}})
    _write(tmp_path / "work/merged/batch-00001.json", {
        "status": "merged", "batch": 1, "source_batch_ref": "source-ref", "source_commit": "67f8551f77807292cebd2b20b2c752b652393835",
    })

    _patch_single_entry_plan(monkeypatch)
    times = iter([
        "2026-08-28T00:00:01Z", "2026-08-28T00:00:02Z", "2026-08-28T00:00:03Z",
        "2026-08-28T00:00:04Z", "2026-08-28T00:00:05Z",
    ])
    monkeypatch.setattr(builder, "utc_now", lambda: next(times))

    first = builder.build_plan(tmp_path, batch_size=20)
    assert first["status"] == "active"
    assert first["changed"] is True
    plan_id = first["plan_id"]
    active_path = tmp_path / "work/translation_review/active_plan.json"
    active_before = active_path.read_text(encoding="utf-8")
    parallel_path = tmp_path / "work/parallel_state.json"
    parallel_before = json.loads(parallel_path.read_text(encoding="utf-8"))
    assert parallel_before["translation_review_gate"]["reason"] == builder.INCOMPLETE_GATE_REASON
    assert parallel_before["translation_review_gate"]["active_plan_id"] == plan_id
    assert parallel_before["translation_review_gate"]["unresolved_entries"] == 1
    assert parallel_before["translation_review_gate"]["claims_allowed"] is True
    assert parallel_before["translation_review_gate"]["concurrent_translation_enabled"] is True
    assert parallel_before["translation_review_gate"]["review_worker_cap"] == 2

    second = builder.build_plan(tmp_path, batch_size=20)
    assert second == {
        "status": "active_plan_incomplete",
        "changed": False,
        "plan_id": plan_id,
        "candidate_count": 1,
        "source_bridge_policy_sha256": "bridge-hash",
        "item_scoped_policy_sha256": "item-policy-hash",
    }
    assert active_path.read_text(encoding="utf-8") == active_before

    parallel_after = json.loads(parallel_path.read_text(encoding="utf-8"))
    before_gate = parallel_before["translation_review_gate"]
    after_gate = parallel_after["translation_review_gate"]
    assert {k: v for k, v in after_gate.items() if k != "updated_at"} == {k: v for k, v in before_gate.items() if k != "updated_at"}
    assert after_gate["updated_at"] != before_gate["updated_at"]
    assert builder.normalize_gate_state_for_noop(parallel_after, parallel_before) == parallel_before


def test_merged_defer_plan_rebuild_gets_new_identity_when_item_context_changes(tmp_path: Path, monkeypatch) -> None:
    """Resolved item context must reopen a previously merged defer batch safely.

    Review merge markers are immutable and keyed by batch id. If a defer remains a
    candidate after its item-scoped canonical context changes, rebuilding with the
    same plan id would recreate the same batch id and the old merged marker would
    make that candidate permanently unclaimable.
    """
    _write(tmp_path / "localized_data/localize_dict.json", {"RaceTest": "Cuộc đua"})
    _write(tmp_path / "work/parallel_state.json", {"translation_review_gate": {"enabled": False}})
    _write(tmp_path / "work/merged/batch-00001.json", {
        "status": "merged", "batch": 1, "source_batch_ref": "source-ref", "source_commit": "67f8551f77807292cebd2b20b2c752b652393835",
    })

    _patch_single_entry_plan(monkeypatch, item_contexts=["item-context-v1", "item-context-v2"])
    counter = iter(range(1, 20))
    monkeypatch.setattr(builder, "utc_now", lambda: f"2026-08-28T00:00:{next(counter):02d}Z")

    first = builder.build_plan(tmp_path, batch_size=20)
    assert first["status"] == "active"
    first_plan_id = str(first["plan_id"])
    first_batch_id = f"{first_plan_id}-b0001"

    # Simulate the authoritative merger accepting a defer-only review batch.
    _write(tmp_path / "work/translation_review/merged" / f"{first_batch_id}.json", {
        "schema_version": 1,
        "status": "merged",
        "plan_id": first_plan_id,
        "batch_id": first_batch_id,
        "counts": {"defer": 1},
        "gate_resolved_items": 0,
        "deferred_items": 1,
    })

    second = builder.build_plan(tmp_path, batch_size=20)
    assert second["status"] == "active"
    second_plan_id = str(second["plan_id"])
    assert second_plan_id != first_plan_id
    assert second["candidate_count"] == 1

    # The reopened candidate now has a fresh batch id, so the prior immutable
    # merged marker cannot suppress the new review claim.
    second_batch_id = f"{second_plan_id}-b0001"
    assert not (tmp_path / "work/translation_review/merged" / f"{second_batch_id}.json").exists()
    active = json.loads((tmp_path / "work/translation_review/active_plan.json").read_text(encoding="utf-8"))
    assert active["plan_id"] == second_plan_id
    assert active["candidate_count"] == 1

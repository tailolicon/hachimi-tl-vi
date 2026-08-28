from __future__ import annotations

import json
from pathlib import Path

import scripts.build_translation_review_plan as builder


def _write(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def test_fresh_plan_then_unchanged_rebuild_is_timestamp_only_and_normalizes_to_noop(tmp_path: Path, monkeypatch) -> None:
    _write(tmp_path / "localized_data/localize_dict.json", {"RaceTest": "Cuộc đua"})
    _write(tmp_path / "work/parallel_state.json", {"translation_review_gate": {"enabled": False}})
    _write(tmp_path / "work/merged/batch-00001.json", {
        "status": "merged", "batch": 1, "source_batch_ref": "source-ref", "source_commit": "67f8551f77807292cebd2b20b2c752b652393835",
    })

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

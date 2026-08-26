from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

from scripts.build_parallel_curation_plan import build_or_extend_plan
from scripts.merge_parallel_curation import merge_speech_batch, merge_term_batch
from scripts import reap_stale_curation_claims as reaper


def test_plan_batches_and_extension_are_stable():
    speech = {
        "source_commit": "a" * 40,
        "characters": [
            {"character_key": str(i), "canonical": f"C{i}", "status": "needs_curated_review", "priority": 10 - i}
            for i in range(1, 7)
        ],
    }
    terms = {
        "source_commit": "a" * 40,
        "review_queue": [
            {"source_zh_cn": f"T{i}", "status": "needs_translation_review", "primary_kind": "skill_name", "priority": 10}
            for i in range(1, 22)
        ],
    }
    plan, stats = build_or_extend_plan(speech, terms)
    assert plan["plan_id"] == "ctx-aaaaaaaaaaaaaaaa-v1"
    assert len(plan["speech_batches"]) == 2
    assert len(plan["terminology_batches"]) == 2
    assert stats == {"speech_batches_added": 2, "terminology_batches_added": 2}

    same, stats2 = build_or_extend_plan(speech, terms, plan)
    assert [b["batch_id"] for b in same["speech_batches"]] == ["speech-0001", "speech-0002"]
    assert [b["batch_id"] for b in same["terminology_batches"]] == ["term-0001", "term-0002"]
    assert stats2 == {"speech_batches_added": 0, "terminology_batches_added": 0}


def test_speech_batch_merges_only_exact_coverage():
    batch = {
        "batch_id": "speech-0001",
        "kind": "speech",
        "items": [{"character_key": "1001", "canonical": "Special Week"}],
    }
    result = {
        "profiles": [
            {
                "character_key": "1001",
                "canonical": "Special Week",
                "register": ["chân thành", "sáng sủa"],
                "tempo": "vừa phải",
                "politeness": "tự nhiên theo scene",
                "translation_rules": ["Giữ câu rõ và chân thành.", "Không tự thêm phương ngữ."],
                "confidence": "high",
            }
        ]
    }
    bible = {"profiles": {}}
    count = merge_speech_batch(
        batch,
        result,
        bible,
        plan_id="ctx-test",
        batch_id="speech-0001",
        claim_id="claim-1",
        worker_id="worker-a",
    )
    assert count == 1
    assert bible["profiles"]["1001"]["status"] == "parallel_curated_review"
    assert bible["profiles"]["1001"]["curation"]["claim_id"] == "claim-1"


def test_terminology_batch_writes_explicit_decisions_only():
    batch = {
        "batch_id": "term-0001",
        "kind": "terminology",
        "items": [
            {"source_zh_cn": "弧线教授", "primary_kind": "skill_name"},
            {"source_zh_cn": "不确定名", "primary_kind": "character_name"},
        ],
    }
    result = {
        "decisions": [
            {"source_zh_cn": "弧线教授", "action": "lock", "target_vi": "Giáo sư Đường cong"},
            {"source_zh_cn": "不确定名", "action": "defer", "note": "Chưa đủ bằng chứng tên riêng."},
        ]
    }
    reviews = {"decisions": []}
    count = merge_term_batch(
        batch,
        result,
        reviews,
        plan_id="ctx-test",
        batch_id="term-0001",
        claim_id="claim-2",
        worker_id="worker-b",
    )
    assert count == 2
    assert reviews["decisions"][0]["action"] == "lock"
    assert reviews["decisions"][0]["kind"] == "skill_name"
    assert reviews["decisions"][1]["action"] == "defer"


def test_reaper_removes_expired_claim(monkeypatch, tmp_path: Path):
    work = tmp_path / "curation"
    claims = work / "claims"
    claims.mkdir(parents=True)
    claim = claims / "speech-0001.json"
    claim.write_text(
        '{"claim_id":"c1","expires_at":"2026-08-26T00:00:00+00:00"}',
        encoding="utf-8",
    )
    monkeypatch.setattr(reaper, "WORK_ROOT", work)
    now = datetime(2026, 8, 26, 1, 0, tzinfo=timezone.utc)
    stats = reaper.reap(now)
    assert stats["expired_removed"] == 1
    assert not claim.exists()

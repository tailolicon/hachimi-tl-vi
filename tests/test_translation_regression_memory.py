from __future__ import annotations

import json
from pathlib import Path

from scripts.build_translation_regression_memory import build


def _write(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def test_builds_memory_only_from_accepted_revisions(tmp_path: Path) -> None:
    plan_id = "tr-test"
    batch_id = "tr-test-b0000"
    claim_id = "claim-1"
    batch_path = f"work/translation_review/batches/{plan_id}/{batch_id}.json"

    _write(
        tmp_path / f"work/translation_review/plans/{plan_id}.json",
        {
            "plan_id": plan_id,
            "batches": [{"batch_id": batch_id, "batch_path": batch_path}],
        },
    )
    _write(
        tmp_path / batch_path,
        {
            "plan_id": plan_id,
            "batch_id": batch_id,
            "items": [
                {
                    "uid": "u-revise",
                    "source_text": "重新启动",
                    "source_fingerprint": "fp1",
                    "current_text": "Khởi chạy lại",
                },
                {
                    "uid": "u-keep",
                    "source_text": "继续",
                    "source_fingerprint": "fp2",
                    "current_text": "Tiếp tục",
                },
                {
                    "uid": "u-deferred",
                    "source_text": "前行",
                    "source_fingerprint": "fp3",
                    "current_text": "Tiến lên",
                },
            ],
        },
    )
    _write(
        tmp_path / f"work/translation_review/results/{batch_id}/{claim_id}.json",
        {
            "decisions": [
                {
                    "uid": "u-revise",
                    "action": "revise",
                    "confidence": "high",
                    "proposed_text": "Khởi động lại",
                    "reason": "Meaning was wrong.",
                },
                {
                    "uid": "u-keep",
                    "action": "keep",
                    "confidence": "high",
                    "reason": "Correct.",
                },
                {
                    "uid": "u-deferred",
                    "action": "revise",
                    "confidence": "high",
                    "proposed_text": "Nhắm Hàng Trước",
                    "reason": "Needs canonical evidence.",
                },
            ]
        },
    )
    _write(
        tmp_path / f"work/translation_review/merged/{batch_id}.json",
        {
            "status": "merged",
            "plan_id": plan_id,
            "batch_id": batch_id,
            "claim_id": claim_id,
            "auto_deferred": [{"uid": "u-deferred", "reasons": ["source_bridge_untrusted_source"]}],
        },
    )

    payload = build(tmp_path)

    assert payload["summary"]["accepted_revision_events"] == 1
    assert payload["summary"]["regression_identity_count"] == 1
    entry = payload["entries"][0]
    assert entry["uid"] == "u-revise"
    assert entry["source_text"] == "重新启动"
    assert entry["rejected_targets"] == ["Khởi chạy lại"]
    assert entry["approved_target"] == "Khởi động lại"


def test_build_output_is_deterministic(tmp_path: Path) -> None:
    first = build(tmp_path)
    first_text = (tmp_path / "glossary/translation_regressions.generated.json").read_text(encoding="utf-8")
    second = build(tmp_path)
    second_text = (tmp_path / "glossary/translation_regressions.generated.json").read_text(encoding="utf-8")
    assert first == second
    assert first_text == second_text

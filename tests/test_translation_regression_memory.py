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
            "merged_at": "2026-08-27T00:00:00Z",
            "auto_deferred": [{"uid": "u-deferred", "reasons": ["source_bridge_untrusted_source"]}],
        },
    )

    payload = build(tmp_path)

    assert payload["summary"]["accepted_revision_events"] == 1
    assert payload["summary"]["accepted_translation_revision_events"] == 1
    assert payload["summary"]["accepted_ui_revision_events"] == 0
    assert payload["summary"]["regression_identity_count"] == 1
    entry = payload["entries"][0]
    assert entry["uid"] == "u-revise"
    assert entry["source_text"] == "重新启动"
    assert entry["rejected_targets"] == ["Khởi chạy lại"]
    assert entry["approved_target"] == "Khởi động lại"
    assert entry["origins"] == ["translation_review"]


def test_builds_memory_from_accepted_ui_revisions(tmp_path: Path) -> None:
    plan_id = "ui-test"
    batch_id = "ui-test-b0001"
    claim_id = "ui-claim-1"
    batch_path = f"work/ui_review/batches/{plan_id}/{batch_id}.json"

    _write(
        tmp_path / f"work/ui_review/plans/{plan_id}.json",
        {"plan_id": plan_id, "batches": [{"batch_id": batch_id, "batch_path": batch_path}]},
    )
    _write(
        tmp_path / batch_path,
        {
            "items": [
                {
                    "key": "Menu424001",
                    "uid": "zhcn:menu",
                    "source_text": "物品/转换",
                    "source_fingerprint": "ui-fp",
                    "current_text": "Vật phẩm/Chuyển đổi",
                    "risk_flags": ["overflow_risk", "verbose_wording"],
                },
                {
                    "key": "IgnoredKeep",
                    "uid": "zhcn:keep",
                    "source_text": "继续",
                    "source_fingerprint": "keep-fp",
                    "current_text": "Tiếp tục",
                    "risk_flags": [],
                },
            ]
        },
    )
    _write(
        tmp_path / f"work/ui_review/results/{batch_id}/{claim_id}.json",
        {
            "decisions": [
                {
                    "key": "Menu424001",
                    "action": "revise",
                    "confidence": "high",
                    "proposed_text": "Vật phẩm / Đổi",
                    "control_type": "menu_tile",
                    "reason": "Old wording overflowed the menu tile.",
                },
                {
                    "key": "IgnoredKeep",
                    "action": "keep",
                    "confidence": "high",
                    "control_type": "button",
                    "reason": "Already compact.",
                },
            ]
        },
    )
    _write(
        tmp_path / f"work/ui_review/merged/{batch_id}.json",
        {
            "status": "merged",
            "plan_id": plan_id,
            "batch_id": batch_id,
            "claim_id": claim_id,
            "merged_at": "2026-08-28T00:00:00Z",
        },
    )

    payload = build(tmp_path)

    assert payload["summary"]["ui_merged_markers_scanned"] == 1
    assert payload["summary"]["accepted_ui_revision_events"] == 1
    assert payload["summary"]["accepted_revision_events"] == 1
    entry = payload["entries"][0]
    assert entry["uid"] == "zhcn:menu"
    assert entry["rejected_targets"] == ["Vật phẩm/Chuyển đổi"]
    assert entry["approved_target"] == "Vật phẩm / Đổi"
    assert entry["origins"] == ["ui_review"]
    assert entry["ui_contexts"] == [
        {
            "key": "Menu424001",
            "control_type": "menu_tile",
            "risk_flags": ["overflow_risk", "verbose_wording"],
        }
    ]
    assert entry["evidence"][0]["origin"] == "ui_review"
    assert entry["evidence"][0]["ui_key"] == "Menu424001"


def test_latest_review_can_intentionally_reapprove_an_older_form(tmp_path: Path) -> None:
    # Translation review: A -> B, then later UI review: B -> A. The unified
    # memory must not hard-block A after the later accepted UI decision.
    tr_plan = "tr-test"
    tr_batch = "tr-test-b1"
    tr_claim = "tr-claim"
    tr_batch_path = f"work/translation_review/batches/{tr_plan}/{tr_batch}.json"
    _write(tmp_path / f"work/translation_review/plans/{tr_plan}.json", {"batches": [{"batch_id": tr_batch, "batch_path": tr_batch_path}]})
    _write(tmp_path / tr_batch_path, {"items": [{"uid": "same", "source_text": "标签", "source_fingerprint": "fp", "current_text": "Dài"}]})
    _write(tmp_path / f"work/translation_review/results/{tr_batch}/{tr_claim}.json", {"decisions": [{"uid": "same", "action": "revise", "confidence": "high", "proposed_text": "Ngắn", "reason": "First review"}]})
    _write(tmp_path / f"work/translation_review/merged/{tr_batch}.json", {"status": "merged", "plan_id": tr_plan, "batch_id": tr_batch, "claim_id": tr_claim, "merged_at": "2026-08-27T00:00:00Z"})

    ui_plan = "ui-test"
    ui_batch = "ui-test-b1"
    ui_claim = "ui-claim"
    ui_batch_path = f"work/ui_review/batches/{ui_plan}/{ui_batch}.json"
    _write(tmp_path / f"work/ui_review/plans/{ui_plan}.json", {"batches": [{"batch_id": ui_batch, "batch_path": ui_batch_path}]})
    _write(tmp_path / ui_batch_path, {"items": [{"key": "Label", "uid": "same", "source_text": "标签", "source_fingerprint": "fp", "current_text": "Ngắn", "risk_flags": ["context_risk"]}]})
    _write(tmp_path / f"work/ui_review/results/{ui_batch}/{ui_claim}.json", {"decisions": [{"key": "Label", "action": "revise", "confidence": "high", "proposed_text": "Dài", "control_type": "label", "reason": "Screen context requires the explicit form"}]})
    _write(tmp_path / f"work/ui_review/merged/{ui_batch}.json", {"status": "merged", "plan_id": ui_plan, "batch_id": ui_batch, "claim_id": ui_claim, "merged_at": "2026-08-28T00:00:00Z"})

    entry = build(tmp_path)["entries"][0]
    assert entry["approved_target"] == "Dài"
    assert entry["rejected_targets"] == ["Ngắn"]
    assert entry["origins"] == ["translation_review", "ui_review"]


def test_build_output_is_deterministic(tmp_path: Path) -> None:
    first = build(tmp_path)
    first_text = (tmp_path / "glossary/translation_regressions.generated.json").read_text(encoding="utf-8")
    second = build(tmp_path)
    second_text = (tmp_path / "glossary/translation_regressions.generated.json").read_text(encoding="utf-8")
    assert first == second
    assert first_text == second_text

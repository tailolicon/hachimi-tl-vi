from __future__ import annotations

import json
from pathlib import Path

from scripts.refresh_translation_review_batch_findings import refresh_active_batches


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def test_refresh_removes_resolved_finding_from_unmerged_batch(tmp_path: Path) -> None:
    review = tmp_path / "work" / "translation_review"
    plan_id = "tr-test"
    batch_id = "tr-test-b0001"
    batch_path = f"work/translation_review/batches/{plan_id}/{batch_id}.json"
    _write(review / "active_plan.json", {"status": "active", "plan_path": f"work/translation_review/plans/{plan_id}.json"})
    _write(review / "plans" / f"{plan_id}.json", {"batches": [{"batch_id": batch_id, "batch_path": batch_path}]})
    _write(tmp_path / batch_path, {"items": [{
        "uid": "power-cap",
        "key": None,
        "source_text": "力量上限提升",
        "source_path": "text_data_dict.json",
        "json_path": ["172", "1"],
        "canonical_findings": [{"finding_id": "cf-power", "source_zh_cn": "力量"}],
        "item_context_sha256": "stale",
    }]})
    _write(tmp_path / "glossary" / "canonical_findings.json", {"findings": [{
        "finding_id": "cf-power",
        "status": "open",
        "source_zh_cn": "力量",
        "match_mode": "contains",
        "source_paths": ["text_data_dict.json"],
        "canonical_resolution": {"layer": "context_guard", "term_id": "common.stat.power", "target_vi": "Power"},
        "review_resolution": None,
    }]})
    _write(tmp_path / "glossary" / "term_registry.json", {"terms": []})
    _write(tmp_path / "glossary" / "ui_community_terms.json", {"terms": []})

    result = refresh_active_batches(tmp_path)
    assert result["changed"] is True
    batch = json.loads((tmp_path / batch_path).read_text(encoding="utf-8"))
    assert batch["items"][0]["canonical_findings"] == []
    assert batch["items"][0]["item_context_sha256"] is None


def test_refresh_does_not_touch_merged_batch(tmp_path: Path) -> None:
    review = tmp_path / "work" / "translation_review"
    plan_id = "tr-test"
    batch_id = "tr-test-b0001"
    batch_path = f"work/translation_review/batches/{plan_id}/{batch_id}.json"
    _write(review / "active_plan.json", {"status": "active", "plan_path": f"work/translation_review/plans/{plan_id}.json"})
    _write(review / "plans" / f"{plan_id}.json", {"batches": [{"batch_id": batch_id, "batch_path": batch_path}]})
    original = {"items": [{"uid": "done", "canonical_findings": [{"finding_id": "cf-power"}], "item_context_sha256": "old"}]}
    _write(tmp_path / batch_path, original)
    _write(review / "merged" / f"{batch_id}.json", {"status": "merged"})
    _write(tmp_path / "glossary" / "canonical_findings.json", {"findings": []})
    _write(tmp_path / "glossary" / "term_registry.json", {"terms": []})
    _write(tmp_path / "glossary" / "ui_community_terms.json", {"terms": []})

    assert refresh_active_batches(tmp_path) == {"changed": False, "updated_batches": 0, "updated_items": 0}
    assert json.loads((tmp_path / batch_path).read_text(encoding="utf-8")) == original

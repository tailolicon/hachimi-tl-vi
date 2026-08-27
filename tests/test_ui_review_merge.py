import json
from pathlib import Path

from scripts.merge_ui_review import _validate_result, merge, terminology_snapshot_hash
from scripts.ui_review_common import text_fingerprint, visual_width


def _write(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _write_term_context(repo: Path) -> None:
    _write(repo / "glossary/term_registry.json", {"schema_version": 1, "terms": []})
    _write(repo / "glossary/ui_community_terms.json", {"schema_version": 1, "policy_version": 3, "terms": []})
    _write(repo / "glossary/ui_short_forms.json", {"schema_version": 1, "terms": []})


def _fixture(
    repo: Path,
    *,
    localized_text: str = "Phòng trưng bày cúp",
    policy_version: int = 3,
) -> tuple[str, str, str]:
    _write_term_context(repo)
    plan_id = f"ui-p{policy_version}-test"
    batch_id = f"{plan_id}-b0001"
    claim_id = "claim-test"
    source = "奖杯陈列室"
    snapshot_text = "Phòng trưng bày cúp"
    fp = text_fingerprint(snapshot_text)
    batch_rel = f"work/ui_review/batches/{plan_id}/{batch_id}.json"

    _write(repo / "localized_data/localize_dict.json", {"Menu0004": localized_text})
    _write(repo / "glossary/ui_overrides.json", {"schema_version": 1, "key_overrides": [], "exact_replacements": []})
    _write(repo / "work/ui_review/reviewed_index.json", {"schema_version": 1, "entries": {}})
    plan = {
        "schema_version": 1,
        "policy_version": policy_version,
        "plan_id": plan_id,
        "batches": [{"batch_id": batch_id, "batch_path": batch_rel, "item_count": 1}],
    }
    if policy_version >= 3:
        plan["terminology_snapshot_sha256"] = terminology_snapshot_hash(repo)
    _write(repo / f"work/ui_review/plans/{plan_id}.json", plan)
    _write(
        repo / batch_rel,
        {
            "schema_version": 1,
            "policy_version": policy_version,
            "plan_id": plan_id,
            "batch_id": batch_id,
            "items": [
                {
                    "key": "Menu0004",
                    "path": ["Menu0004"],
                    "source_text": source,
                    "source_fingerprint": "source-fp",
                    "current_text": snapshot_text,
                    "current_fingerprint": fp,
                    "source_visual_width": visual_width(source),
                    "current_visual_width": visual_width(snapshot_text),
                    "community_terms": [],
                }
            ],
        },
    )
    result_rel = f"work/ui_review/results/{batch_id}/{claim_id}.json"
    _write(
        repo / result_rel,
        {
            "schema_version": 1,
            "plan_id": plan_id,
            "batch_id": batch_id,
            "claim_id": claim_id,
            "worker_id": "pytest",
            "reviewed_at": "2026-08-26T00:00:00Z",
            "decisions": [
                {
                    "key": "Menu0004",
                    "current_fingerprint": fp,
                    "action": "revise",
                    "proposed_text": "Tủ cúp",
                    "control_type": "menu_tile",
                    "reason": "Shorter fixed-size menu label.",
                    "confidence": "high",
                }
            ],
        },
    )
    _write(
        repo / f"work/ui_review/completions/{batch_id}/{claim_id}.json",
        {
            "schema_version": 1,
            "plan_id": plan_id,
            "batch_id": batch_id,
            "claim_id": claim_id,
            "worker_id": "pytest",
            "result_path": result_rel,
            "completed_at": "2026-08-26T00:00:00Z",
        },
    )
    return plan_id, batch_id, claim_id


def test_merge_applies_v3_revision_and_persists_override(tmp_path: Path):
    _, batch_id, _ = _fixture(tmp_path)
    report = merge(tmp_path)
    localized = json.loads((tmp_path / "localized_data/localize_dict.json").read_text(encoding="utf-8"))
    overrides = json.loads((tmp_path / "glossary/ui_overrides.json").read_text(encoding="utf-8"))
    reviewed = json.loads((tmp_path / "work/ui_review/reviewed_index.json").read_text(encoding="utf-8"))
    marker = json.loads((tmp_path / f"work/ui_review/merged/{batch_id}.json").read_text(encoding="utf-8"))

    assert report["counts"]["revise"] == 1
    assert localized["Menu0004"] == "Tủ cúp"
    assert any(item.get("path") == ["Menu0004"] and item.get("text") == "Tủ cúp" for item in overrides["key_overrides"])
    assert reviewed["entries"]["Menu0004"]["current_fingerprint"] == text_fingerprint("Tủ cúp")
    assert reviewed["entries"]["Menu0004"]["policy_version"] == 3
    assert marker["status"] == "merged"


def test_merge_closes_stale_batch_without_applying_old_revision(tmp_path: Path):
    _, batch_id, _ = _fixture(tmp_path, localized_text="Đã đổi ở main")
    report = merge(tmp_path)
    localized = json.loads((tmp_path / "localized_data/localize_dict.json").read_text(encoding="utf-8"))
    marker = json.loads((tmp_path / f"work/ui_review/merged/{batch_id}.json").read_text(encoding="utf-8"))

    assert report["stale_batches"][0]["batch_id"] == batch_id
    assert localized["Menu0004"] == "Đã đổi ở main"
    assert marker["status"] == "stale"


def test_merge_supersedes_pre_v3_completion(tmp_path: Path):
    _, batch_id, _ = _fixture(tmp_path, policy_version=2)
    report = merge(tmp_path)
    localized = json.loads((tmp_path / "localized_data/localize_dict.json").read_text(encoding="utf-8"))
    marker = json.loads((tmp_path / f"work/ui_review/merged/{batch_id}.json").read_text(encoding="utf-8"))

    assert localized["Menu0004"] == "Phòng trưng bày cúp"
    assert report["superseded_batches"] == [{"batch_id": batch_id, "reason": "legacy_policy"}]
    assert marker["status"] == "superseded"


def test_validator_rejects_forbidden_community_calque_and_requires_basis():
    fp = text_fingerprint("Chi tiết Thanh Anh hùng")
    batch = {
        "items": [
            {
                "key": "Heroes511003",
                "source_text": "英雄量表详情",
                "current_text": "Chi tiết Thanh Anh hùng",
                "current_fingerprint": fp,
                "source_visual_width": 6.0,
                "current_visual_width": 12.34,
                "community_terms": [
                    {
                        "id": "event.loh.hero_gauge",
                        "accepted": ["Hero Gauge"],
                        "forbidden": ["Thanh Anh hùng"],
                        "require_accepted": True,
                    }
                ],
            }
        ]
    }
    completion = {
        "plan_id": "ui-p3-test",
        "batch_id": "ui-p3-test-b0001",
        "claim_id": "claim",
        "worker_id": "pytest",
    }
    result = {
        **completion,
        "decisions": [
            {
                "key": "Heroes511003",
                "current_fingerprint": fp,
                "action": "keep",
                "control_type": "header",
                "reason": "Looks short enough.",
                "confidence": "high",
            }
        ],
    }

    _, errors = _validate_result(completion, result, batch)
    assert any("terminology_basis is required" in error for error in errors)
    assert any("forbidden/noncanonical wording" in error for error in errors)
    assert any("accepted player-facing form" in error for error in errors)

    result["decisions"][0] = {
        "key": "Heroes511003",
        "current_fingerprint": fp,
        "action": "revise",
        "proposed_text": "Chi tiết Hero Gauge",
        "control_type": "header",
        "reason": "Use the named LoH mechanic.",
        "terminology_basis": "ui_community_terms:event.loh.hero_gauge",
        "confidence": "high",
    }
    _, errors = _validate_result(completion, result, batch)
    assert not errors

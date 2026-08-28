from __future__ import annotations

import json
from pathlib import Path

from scripts.build_source_bridge_risk_registry import build_registry, is_confirmed_lossy_note


def _write_result(root: Path, name: str, decisions: list[dict]) -> None:
    path = root / "term-0001" / f"{name}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "batch_id": "term-0001",
                "claim_id": name,
                "decisions": decisions,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def test_strong_lossy_defer_is_promoted_but_generic_ambiguity_is_not(tmp_path: Path) -> None:
    results = tmp_path / "results"
    _write_result(
        results,
        "claim-a",
        [
            {
                "source_zh_cn": "一线曙光",
                "action": "defer",
                "note": "The zh-CN title changes the image to a ray of dawn, so it is unsafe to lock from the semantic bridge.",
            },
            {
                "source_zh_cn": "一番星",
                "action": "defer",
                "note": "Several natural Vietnamese renderings are plausible; defer until a stable convention is chosen.",
            },
            {
                "source_zh_cn": "锁定例",
                "action": "lock",
                "target_vi": "Ví dụ",
                "note": "The zh-CN title changes the image, but this is a lock decision and must not enter risk mining.",
            },
        ],
    )

    output = build_registry(results, {"terms": []}, {"canonical_examples": []})
    sources = [item["zh_cn_exact"][0] for item in output["untrusted_sources"]]

    assert sources == ["一线曙光"]
    assert output["summary"]["scanned_decisions"] == 3
    assert output["summary"]["deferred_decisions"] == 2
    assert output["summary"]["strong_evidence_decisions"] == 1


def test_sources_already_canonical_are_excluded(tmp_path: Path) -> None:
    results = tmp_path / "results"
    _write_result(
        results,
        "claim-b",
        [
            {
                "source_zh_cn": "一阵狂风",
                "action": "defer",
                "note": "The source replaces the JP nuance and should not be translated literally.",
            },
            {
                "source_zh_cn": "一飞冲天！",
                "action": "defer",
                "note": "The zh-CN title changes the JP wording and is interpretive.",
            },
        ],
    )
    registry = {
        "terms": [
            {
                "id": "skill.example",
                "zh_cn": ["一阵狂风"],
                "target_vi": "Một cơn gió",
                "locked": True,
            }
        ]
    }
    style = {
        "canonical_examples": [
            {
                "source_zh_cn": "一飞冲天！",
                "target_vi": "Nhất định sẽ bay được!",
            }
        ]
    }

    output = build_registry(results, registry, style)

    assert output["untrusted_sources"] == []
    assert output["summary"]["strong_evidence_decisions"] == 2
    assert output["summary"]["skipped_already_canonical"] == 2


def test_evidence_is_deduplicated_and_output_is_deterministic(tmp_path: Path) -> None:
    results = tmp_path / "results"
    decision = {
        "source_zh_cn": "一跃而上",
        "action": "defer",
        "note": "The zh-CN title is not title-equivalent to JP, so defer instead of translating the bridge literally.",
    }
    _write_result(results, "claim-c", [decision, decision])

    first = build_registry(results, {"terms": []}, {"canonical_examples": []})
    second = build_registry(results, {"terms": []}, {"canonical_examples": []})

    assert first == second
    assert len(first["untrusted_sources"]) == 1
    assert len(first["untrusted_sources"][0]["evidence"]) == 1


def test_classifier_does_not_promote_plain_uncertainty() -> None:
    assert is_confirmed_lossy_note("The source shifts the nuance from A to B; defer.")
    assert is_confirmed_lossy_note("Pinned skill is JP X. The zh-CN title is not title-equivalent.")
    assert not is_confirmed_lossy_note("The exact Japanese title was not verified strongly enough; defer.")
    assert not is_confirmed_lossy_note("Several Vietnamese renderings are plausible.")

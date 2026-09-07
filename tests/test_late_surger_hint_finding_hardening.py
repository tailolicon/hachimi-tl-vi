from __future__ import annotations

import json
from pathlib import Path

from scripts.harden_late_surger_hint_finding import NOTE, TARGET, TERM_ID, harden


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def test_hardener_repairs_registry_and_review_lock_idempotently(tmp_path: Path) -> None:
    registry_path = tmp_path / "glossary" / "term_registry.json"
    reviews_path = tmp_path / "glossary" / "terminology_reviews.json"
    _write(
        registry_path,
        {
            "schema_version": 2,
            "terms": [
                {
                    "id": TERM_ID,
                    "category": "skill_name",
                    "zh_cn": ["居中诀窍○"],
                    "target_vi": "Mẹo Sashi○",
                    "locked": True,
                }
            ],
        },
    )
    _write(
        reviews_path,
        {
            "schema_version": 1,
            "decisions": [
                {
                    "decision_id": "legacy-sashi-hint",
                    "source_zh_cn": "居中诀窍○",
                    "action": "lock",
                    "target_vi": "Mẹo Sashi○",
                    "kind": "skill_name",
                },
                {
                    "decision_id": "unrelated",
                    "source_zh_cn": "逃亡者",
                    "action": "lock",
                    "target_vi": "Kẻ Đào Tẩu",
                },
            ],
        },
    )

    assert harden(tmp_path) is True
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    reviews = json.loads(reviews_path.read_text(encoding="utf-8"))
    term = registry["terms"][0]
    decision = reviews["decisions"][0]
    assert term["target_vi"] == TARGET
    assert term["note"] == NOTE
    assert decision["target_vi"] == TARGET
    assert decision["note"] == NOTE
    assert reviews["decisions"][1]["target_vi"] == "Kẻ Đào Tẩu"

    before_registry = registry_path.read_text(encoding="utf-8")
    before_reviews = reviews_path.read_text(encoding="utf-8")
    assert harden(tmp_path) is False
    assert registry_path.read_text(encoding="utf-8") == before_registry
    assert reviews_path.read_text(encoding="utf-8") == before_reviews

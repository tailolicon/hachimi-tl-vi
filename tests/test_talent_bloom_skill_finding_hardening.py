from __future__ import annotations

import json
from pathlib import Path

from scripts.harden_talent_bloom_skill_finding import TERM_ID, harden
from scripts.translation_review_common import load_locked_terms, locked_term_matches


def _write_registry(root: Path) -> None:
    glossary = root / "glossary"
    glossary.mkdir(parents=True)
    (glossary / "term_registry.json").write_text(
        json.dumps(
            {
                "terms": [
                    {
                        "id": TERM_ID,
                        "category": "skill_name",
                        "zh_cn": ["开花"],
                        "target_vi": "Nở rộ",
                        "locked": True,
                    }
                ]
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def test_hardener_makes_bloom_skill_exact_and_idempotent(tmp_path: Path) -> None:
    _write_registry(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    terms = load_locked_terms(tmp_path)
    exact = locked_term_matches("开花", "Nở rộ", terms, source_path="text_data_dict.json", json_path=["147", "1"])
    progression = locked_term_matches(
        "用于解锁育成赛马娘或才能开花。",
        "Dùng để mở khóa Mã Nương huấn luyện hoặc Nở rộ tài năng.",
        terms,
        source_path="text_data_dict.json",
        json_path=["114", "114501"],
    )
    assert [item["id"] for item in exact] == [TERM_ID]
    assert progression == []

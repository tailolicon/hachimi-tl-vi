from __future__ import annotations

import json
from pathlib import Path

from scripts.harden_full_effort_skill_finding import TERM_ID, harden
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
                        "zh_cn": ["全力"],
                        "target_vi": "Dốc hết sức",
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


def test_hardener_makes_full_effort_skill_exact_and_idempotent(tmp_path: Path) -> None:
    _write_registry(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    terms = load_locked_terms(tmp_path)
    exact = locked_term_matches("全力", "Dốc hết sức", terms, source_path="text_data_dict.json", json_path=["147", "1"])
    prose = locked_term_matches(
        "因动摇而脚步不稳，无法在英里赛事中发挥全力",
        "Vì dao động nên không thể phát huy toàn lực ở cuộc đua Mile",
        terms,
        source_path="text_data_dict.json",
        json_path=["143", "44"],
    )
    assert [item["id"] for item in exact] == [TERM_ID]
    assert prose == []

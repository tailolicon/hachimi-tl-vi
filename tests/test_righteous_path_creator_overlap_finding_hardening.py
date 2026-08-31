from __future__ import annotations

import json
from pathlib import Path

from scripts.harden_righteous_path_creator_overlap_finding import TERM_ID, harden
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
                        "zh_cn": ["正道"],
                        "target_vi": "Chính đạo",
                        "locked": True,
                    }
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def test_righteous_path_hardener_preserves_skill_and_excludes_creator_name(tmp_path: Path) -> None:
    _write_registry(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    terms = load_locked_terms(tmp_path)
    skill = locked_term_matches(
        "正道",
        "Chính đạo",
        terms,
        source_path="text_data_dict.json",
        json_path=["147", "107701211"],
    )
    creator_credit = locked_term_matches(
        "作词・作曲・编曲：永井正道\\n译：南千和（Bilibili）",
        "Lời ・ Sáng tác ・ Phối khí: 永井正道\\nDịch: 南千和（Bilibili）",
        terms,
        source_path="text_data_dict.json",
        json_path=["17", "1025"],
    )

    assert skill[0]["id"] == TERM_ID
    assert creator_credit == []

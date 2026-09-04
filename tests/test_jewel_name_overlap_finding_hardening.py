from __future__ import annotations

import json
from pathlib import Path

from scripts.harden_jewel_name_overlap_finding import TERM_ID, harden
from scripts.translation_review_common import load_locked_terms, locked_term_matches


def _write_registry(root: Path) -> None:
    glossary = root / "glossary"
    glossary.mkdir(parents=True)
    (glossary / "term_registry.json").write_text(
        json.dumps({
            "terms": [{
                "id": TERM_ID,
                "category": "currency",
                "zh_cn": ["宝石"],
                "target_vi": "Jewel",
                "locked": True,
            }]
        }, ensure_ascii=False),
        encoding="utf-8",
    )


def test_jewel_hardener_preserves_currency_and_excludes_character_name(tmp_path: Path) -> None:
    _write_registry(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False
    terms = load_locked_terms(tmp_path)
    currency = locked_term_matches(
        "获得宝石100个",
        "Nhận 100 Jewel",
        terms,
        source_path="localize_dict.json",
        json_path=["Shop0001"],
    )
    character = locked_term_matches(
        "第一红宝石制作的手工巧克力。",
        "Chocolate thủ công do Daiichi Ruby làm.",
        terms,
        source_path="text_data_dict.json",
        json_path=["10", "10148"],
    )
    emerald = locked_term_matches(
        "碧波间的绿宝石",
        "Ngọc Lục Bảo Giữa Sóng Biếc",
        terms,
        source_path="text_data_dict.json",
        json_path=["14", "100230"],
    )
    sapphire = locked_term_matches(
        "假日・蓝宝石",
        "Ngày nghỉ・Sapphire",
        terms,
        source_path="text_data_dict.json",
        json_path=["14", "105923"],
    )
    assert currency[0]["id"] == TERM_ID
    assert character == []
    assert emerald == []
    assert sapphire == []

from __future__ import annotations

import json
from pathlib import Path

from scripts.harden_recovery_spirit_context_finding import TERM_ID, harden
from scripts.translation_review_common import load_locked_terms, locked_term_matches


def _write_registry(root: Path) -> None:
    glossary = root / "glossary"
    glossary.mkdir(parents=True)
    (glossary / "term_registry.json").write_text(
        json.dumps({"terms": [{
            "id": TERM_ID,
            "category": "condition",
            "zh_cn": ["恢复精神"],
            "target_vi": "Recovery Spirit",
            "locked": True,
        }]}, ensure_ascii=False),
        encoding="utf-8",
    )


def test_recovery_spirit_is_condition_table_only(tmp_path: Path) -> None:
    _write_registry(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False
    terms = load_locked_terms(tmp_path)
    named = locked_term_matches(
        "恢复精神", "Recovery Spirit", terms,
        source_path="text_data_dict.json", json_path=["142", "43"],
    )
    prose = locked_term_matches(
        "喝了恢复精神吧！\n使用后TP恢复30。",
        "Uống để lấy lại tinh thần!\nKhi dùng, hồi 30 TP.",
        terms,
        source_path="text_data_dict.json", json_path=["10", "32"],
    )
    assert named[0]["id"] == TERM_ID
    assert prose == []

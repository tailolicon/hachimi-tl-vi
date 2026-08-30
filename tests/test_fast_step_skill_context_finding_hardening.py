from __future__ import annotations

import json
from pathlib import Path

from scripts.harden_fast_step_skill_context_finding import TERM_ID, harden
from scripts.translation_review_common import load_locked_terms, locked_term_matches


def test_fast_step_skill_is_exact_only(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir(parents=True)
    (glossary / "term_registry.json").write_text(json.dumps({"terms": [{
        "id": TERM_ID,
        "zh_cn": ["快人一步"],
        "target_vi": "Một bước vượt lên",
        "locked": True,
    }]}, ensure_ascii=False), encoding="utf-8")
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False
    terms = load_locked_terms(tmp_path)
    assert locked_term_matches("快人一步", "Một bước vượt lên", terms)[0]["id"] == TERM_ID
    assert locked_term_matches(
        "融会贯通的速度快人一步！", "Nhờ tinh thông mọi thứ, tốc độ luôn đi trước một bước!", terms,
        source_path="text_data_dict.json", json_path=["143", "7"],
    ) == []

from __future__ import annotations

import json
from pathlib import Path

from scripts.harden_innovation_skill_context_finding import TERM_ID, harden
from scripts.translation_review_common import load_locked_terms, locked_term_matches


def _write_registry(root: Path) -> None:
    glossary = root / "glossary"
    glossary.mkdir(parents=True)
    (glossary / "term_registry.json").write_text(
        json.dumps({"terms": [{
            "id": TERM_ID,
            "category": "skill_name",
            "zh_cn": ["革新"],
            "target_vi": "Đổi mới",
            "locked": True,
        }]}, ensure_ascii=False), encoding="utf-8"
    )


def test_innovation_skill_is_exact_only(tmp_path: Path) -> None:
    _write_registry(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False
    terms = load_locked_terms(tmp_path)
    skill = locked_term_matches("革新", "Đổi mới", terms, source_path="text_data_dict.json", json_path=["147", "1"])
    prose = locked_term_matches(
        "掀起一场革新，不是吗！", "Phải tạo nên một cuộc cách mạng chứ!", terms,
        source_path="text_data_dict.json", json_path=["163", "1138"],
    )
    assert skill[0]["id"] == TERM_ID
    assert prose == []

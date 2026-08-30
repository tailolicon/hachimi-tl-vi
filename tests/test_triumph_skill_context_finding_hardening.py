from __future__ import annotations

import json
from pathlib import Path

from scripts.harden_triumph_skill_context_finding import TERM_ID, harden
from scripts.translation_review_common import load_locked_terms, locked_term_matches


def test_triumph_skill_does_not_match_arc_race_name(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir(parents=True)
    (glossary / "term_registry.json").write_text(json.dumps({"terms": [{
        "id": TERM_ID,
        "zh_cn": ["凯旋"],
        "target_vi": "Khải hoàn",
        "locked": True,
    }]}, ensure_ascii=False), encoding="utf-8")
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False
    terms = load_locked_terms(tmp_path)
    assert locked_term_matches("凯旋", "Khải hoàn", terms)[0]["id"] == TERM_ID
    assert locked_term_matches(
        "取得凯旋门赏的胜利", "Chiến thắng Prix de l'Arc de Triomphe", terms,
        source_path="text_data_dict.json", json_path=["131", "291"],
    ) == []

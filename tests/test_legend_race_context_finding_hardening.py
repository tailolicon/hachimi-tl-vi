from __future__ import annotations

import json
from pathlib import Path

from scripts.harden_legend_race_context_finding import TERM_ID, harden
from scripts.translation_review_common import load_locked_terms, locked_term_matches


def test_generic_race_does_not_match_legend_race(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir(parents=True)
    (glossary / "term_registry.json").write_text(json.dumps({"terms": [{
        "id": TERM_ID,
        "zh_cn": ["比赛"],
        "target_vi": "Cuộc đua",
        "locked": True,
    }]}, ensure_ascii=False), encoding="utf-8")
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False
    terms = load_locked_terms(tmp_path)
    assert locked_term_matches("目标比赛", "Cuộc đua mục tiêu", terms)[0]["id"] == TERM_ID
    assert locked_term_matches(
        "参加传奇比赛", "Tham gia Legend Race", terms,
        source_path="localize_dict.json", json_path=["LegendRace0001"],
    ) == []

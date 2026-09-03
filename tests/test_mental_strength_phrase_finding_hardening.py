from __future__ import annotations

import json
from pathlib import Path

from scripts.harden_mental_strength_phrase_finding import POWER_TERM_ID, TERM_ID, harden
from scripts.translation_review_common import community_term_matches, load_community_terms


def _write_terms(root: Path) -> None:
    glossary = root / "glossary"
    glossary.mkdir(parents=True)
    (glossary / "ui_community_terms.json").write_text(
        json.dumps(
            {
                "terms": [
                    {
                        "id": POWER_TERM_ID,
                        "category": "stat",
                        "source_aliases": ["パワー", "力量"],
                        "preferred": "Power",
                        "accepted": ["Power"],
                        "forbidden": ["Sức mạnh"],
                        "require_accepted": True,
                    }
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def test_mental_strength_exact_phrase_beats_power_substring_without_overmatching(tmp_path: Path) -> None:
    _write_terms(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False
    terms = load_community_terms(tmp_path)

    exact = community_term_matches(
        None,
        "精神力量",
        "Sức mạnh tinh thần",
        terms,
        source_path="text_data_dict.json",
        json_path=["147", "3100801"],
    )
    longer = community_term_matches(
        None,
        "精神力量很重要",
        "Sức mạnh tinh thần rất quan trọng",
        terms,
        source_path="text_data_dict.json",
        json_path=["147", "999"],
    )
    stat = community_term_matches(
        None,
        "力量",
        "Power",
        terms,
        source_path="text_data_dict.json",
        json_path=["172", "1"],
    )

    assert [row["id"] for row in exact] == [TERM_ID]
    assert exact[0]["preferred"] == "Sức mạnh tinh thần"
    assert longer == []
    assert stat[0]["id"] == POWER_TERM_ID
    assert stat[0]["preferred"] == "Power"

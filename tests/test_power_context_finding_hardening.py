from __future__ import annotations

import json
from pathlib import Path

from scripts.harden_power_context_finding import TERM_ID, harden
from scripts.translation_review_common import community_term_matches, load_community_terms


def _write_terms(root: Path) -> None:
    glossary = root / "glossary"
    glossary.mkdir(parents=True)
    (glossary / "ui_community_terms.json").write_text(
        json.dumps(
            {
                "terms": [
                    {
                        "id": TERM_ID,
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
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def test_power_context_hardening_preserves_stat_and_excludes_narrative(tmp_path: Path) -> None:
    _write_terms(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    terms = load_community_terms(tmp_path)
    stat = community_term_matches(
        None,
        "力量",
        "Sức mạnh",
        terms,
        source_path="text_data_dict.json",
        json_path=["172", "1"],
    )
    narrative_title = community_term_matches(
        None,
        "商品的力量",
        "Sức mạnh của hàng hóa",
        terms,
        source_path="text_data_dict.json",
        json_path=["130", "181"],
    )
    narrative_item = community_term_matches(
        None,
        "具有激发不可思议力量的能力。",
        "Có khả năng khơi dậy sức mạnh kỳ diệu.",
        terms,
        source_path="text_data_dict.json",
        json_path=["10", "110"],
    )
    assert stat[0]["id"] == TERM_ID
    assert stat[0]["preferred"] == "Power"
    assert narrative_title == []
    assert narrative_item == []

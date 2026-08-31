from __future__ import annotations

import json
from pathlib import Path

from scripts.harden_dirt_surface_finding import SOURCE_ALIAS, TERM_ID, harden
from scripts.translation_review_common import community_term_matches, load_community_terms


def test_zhcn_sand_surface_maps_to_dirt(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir(parents=True)
    (glossary / "ui_community_terms.json").write_text(json.dumps({
        "terms": [{
            "id": TERM_ID,
            "source_aliases": ["ダート"],
            "preferred": "Dirt",
            "accepted": ["Dirt"],
            "forbidden": ["sân cát"],
            "require_accepted": True,
        }],
    }, ensure_ascii=False), encoding="utf-8")

    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    payload = json.loads((glossary / "ui_community_terms.json").read_text(encoding="utf-8"))
    term = payload["terms"][0]
    assert SOURCE_ALIAS in term["source_aliases"]

    terms = load_community_terms(tmp_path)
    matches = community_term_matches(
        None,
        "在草地与沙土的GⅠ级别比赛中各获得3次以上胜利",
        "Giành ít nhất 3 chiến thắng ở các cuộc đua G1 trên Turf và Dirt",
        terms,
        source_path="text_data_dict.json",
        json_path=["131", "71"],
    )
    dirt = next(match for match in matches if match["id"] == TERM_ID)
    assert dirt["accepted_present"] is True
    assert dirt["forbidden_present"] is False

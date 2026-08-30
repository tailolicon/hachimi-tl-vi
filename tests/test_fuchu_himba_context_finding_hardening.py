from __future__ import annotations

import json
from pathlib import Path

from scripts.harden_fuchu_himba_context_finding import TERM_ID, harden
from scripts.translation_review_common import community_term_matches, load_community_terms


def test_generic_umamusume_does_not_match_fuchu_himba_stakes(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir(parents=True)
    (glossary / "ui_community_terms.json").write_text(json.dumps({"terms": [{
        "id": TERM_ID,
        "source_aliases": ["赛马娘"],
        "preferred": "Mã Nương",
        "accepted": ["Mã Nương"],
        "forbidden": ["Uma Musume"],
        "require_accepted": True,
    }]}, ensure_ascii=False), encoding="utf-8")
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False
    terms = load_community_terms(tmp_path)
    generic = community_term_matches(None, "赛马娘", "Mã Nương", terms, source_path="text_data_dict.json", json_path=["1", "1"])
    race = community_term_matches(None, "取得府中赛马娘锦标的胜利", "Chiến thắng Fuchu Himba Stakes", terms, source_path="text_data_dict.json", json_path=["131", "314"])
    assert generic[0]["id"] == TERM_ID
    assert race == []

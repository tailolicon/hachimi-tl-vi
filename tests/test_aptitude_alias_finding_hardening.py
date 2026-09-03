from __future__ import annotations

import json
from pathlib import Path

from scripts.harden_aptitude_alias_finding import TERM, harden
from scripts.translation_review_common import community_term_matches, load_community_terms


def _write_terms(root: Path) -> None:
    glossary = root / "glossary"
    glossary.mkdir(parents=True)
    (glossary / "ui_community_terms.json").write_text('{"terms": []}\n', encoding="utf-8")


def test_aptitude_alias_is_localize_scoped_and_idempotent(tmp_path: Path) -> None:
    _write_terms(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False
    terms = load_community_terms(tmp_path)
    matched = community_term_matches(
        "Race0517",
        "距离适应性不合适而导致没能发挥出能力呢。",
        "Do độ thích nghi cự ly không phù hợp nên chưa thể phát huy khả năng.",
        terms,
        source_path="localize_dict.json",
        json_path=["Race0517"],
    )
    aptitude_variant = community_term_matches(
        "SingleMode701028",
        "由于要出战资质较低的比赛，\n可能会消耗大量闹钟。\n是否直接开始？",
        "Vì sẽ tham gia Cuộc đua có tư chất thấp,\ncó thể tiêu tốn nhiều Đồng hồ báo thức.\nBạn có muốn bắt đầu ngay không?",
        terms,
        source_path="localize_dict.json",
        json_path=["SingleMode701028"],
    )
    unrelated = community_term_matches(
        None,
        "适应性很强",
        "Khả năng thích nghi rất tốt",
        terms,
        source_path="story/data/example.json",
        json_path=["text"],
    )
    assert matched[0]["id"] == TERM["id"]
    assert matched[0]["preferred"] == "Aptitude"
    assert aptitude_variant[0]["id"] == TERM["id"]
    assert aptitude_variant[0]["preferred"] == "Aptitude"
    assert unrelated == []

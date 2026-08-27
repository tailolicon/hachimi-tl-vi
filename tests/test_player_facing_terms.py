from __future__ import annotations

import json
from pathlib import Path

from hachimi_tl_vi.model import SourceEntry
from hachimi_tl_vi.translators.prompt import build_messages
from scripts.build_ui_review_plan import _term_risk, community_term_matches


ROOT = Path(__file__).resolve().parents[1]


def _terms():
    payload = json.loads((ROOT / "glossary/ui_community_terms.json").read_text(encoding="utf-8"))
    return payload["terms"]


def test_common_en_terms_override_old_vietnamese_calques_for_ui_review() -> None:
    cases = [
        ("速度", "Tốc độ", "Speed"),
        ("耐力", "Thể lực", "Stamina"),
        ("根性", "Ý chí", "Guts"),
        ("賢さ", "Trí tuệ", "Wit"),
        ("草地", "Sân cỏ", "Turf"),
        ("短距离", "Cự ly ngắn", "Sprint"),
        ("逃げ", "Nige", "Front Runner"),
    ]
    terms = _terms()
    for source, current, preferred in cases:
        matches = community_term_matches("PolicyTest", source, current, terms)
        assert matches, source
        assert any(match["preferred"] == preferred for match in matches)
        flags, score = _term_risk(matches)
        assert "community_term_mismatch" in flags
        assert score > 0


def test_translation_prompt_injects_player_facing_terminology_before_term_registry() -> None:
    entry = SourceEntry(
        uid="zhcn:policy-test",
        kind="ui",
        source_text="速度",
        locator={},
        context={"source_language": "zh-CN"},
    )
    messages = build_messages([entry], glossary_dir=ROOT / "glossary")
    payload = json.loads(messages[1]["content"])
    assert "player_facing_terminology" in payload
    assert any(
        term.get("id") == "common.stat.speed" and term.get("preferred") == "Speed"
        for term in payload["player_facing_terminology"]["terms"]
    )
    system = messages[0]["content"]
    assert "player_facing_terminology" in system
    assert "ưu tiên CAO NHẤT" in system


def test_skill_policy_keeps_category_english_but_localizes_individual_skill_names() -> None:
    style = json.loads((ROOT / "glossary/style_rules.json").read_text(encoding="utf-8"))
    rules = "\n".join(style["kinds"]["skill"])
    assert "Skill, Unique Skill, Evolution Skill" in rules
    assert "Tên RIÊNG của skill phải được Việt hóa" in rules
    assert "Hán-Việt" in rules
    assert "LoL" in rules

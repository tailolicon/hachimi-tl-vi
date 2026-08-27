from __future__ import annotations

import json
from pathlib import Path

from hachimi_tl_vi.model import SourceEntry
from hachimi_tl_vi.translators.prompt import apply_skill_name_style_overrides, build_messages
from scripts.build_ui_review_plan import _term_risk, community_term_matches, terminology_snapshot_hash


ROOT = Path(__file__).resolve().parents[1]


def _terms():
    payload = json.loads((ROOT / "glossary/ui_community_terms.json").read_text(encoding="utf-8"))
    return payload["terms"]


def _skill_style():
    return json.loads((ROOT / "glossary/skill_name_style.json").read_text(encoding="utf-8"))


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


def test_translation_prompt_injects_player_and_skill_name_policies() -> None:
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
    assert "skill_name_style" in payload
    assert any(
        term.get("id") == "common.stat.speed" and term.get("preferred") == "Speed"
        for term in payload["player_facing_terminology"]["terms"]
    )
    canonical = {
        item["source_zh_cn"]: item["target_vi"]
        for item in payload["skill_name_style"]["canonical_examples"]
    }
    assert canonical["弧线教授"] == "Giáo Sư Cung Tuyến"
    assert canonical["强攻策"] == "Cường Công Kế"
    system = messages[0]["content"]
    assert "player_facing_terminology" in system
    assert "skill_name_style" in system
    assert "弧线教授 -> Giáo Sư Cung Tuyến" in system


def test_skill_policy_follows_compact_chinese_title_rhythm() -> None:
    style = json.loads((ROOT / "glossary/style_rules.json").read_text(encoding="utf-8"))
    rules = "\n".join(style["kinds"]["skill"])
    assert "Skill, Unique Skill, Evolution Skill" in rules
    assert "skill_name_style.json" in rules
    assert "2-4" in rules
    assert "Hán-Việt" in rules
    assert "LoL" in rules
    assert "Giáo Sư" in rules
    assert "Cường Công Kế" in rules


def test_skill_style_exact_examples_are_reviewed_overrides() -> None:
    policy = _skill_style()
    canonical = {item["source_zh_cn"]: item["target_vi"] for item in policy["canonical_examples"]}
    assert canonical["弧线教授"] == "Giáo Sư Cung Tuyến"
    assert canonical["弯道加速○"] == "Gia Tốc Khúc Cua○"
    assert canonical["弯道回复○"] == "Hồi Phục Khúc Cua○"
    assert canonical["弯道巧者○"] == "Xảo Thủ Khúc Cua○"
    assert canonical["强攻策"] == "Cường Công Kế"
    assert "older conflicting skill-name target" in policy["precedence"][0]


def test_prompt_registry_overlay_removes_conflicting_old_skill_lock() -> None:
    old_registry = {
        "schema_version": 2,
        "terms": [
            {
                "id": "skill.corner_professor",
                "category": "skill_name",
                "zh_cn": ["弧线教授"],
                "ja": ["弧線のプロフェッサー"],
                "target_vi": "Giáo sư đường cong",
                "locked": True,
            }
        ],
    }
    effective = apply_skill_name_style_overrides(old_registry, _skill_style())
    term = effective["terms"][0]
    assert term["target_vi"] == "Giáo Sư Cung Tuyến"
    assert term["skill_name_style_override"]["source"] == "glossary/skill_name_style.json"
    assert old_registry["terms"][0]["target_vi"] == "Giáo sư đường cong"


def test_skill_style_changes_ui_terminology_snapshot() -> None:
    # The builder hashes the policy file, so changing approved skill-title policy
    # supersedes a plan that was reviewed against an older terminology snapshot.
    before = terminology_snapshot_hash(ROOT)
    skill_path = ROOT / "glossary/skill_name_style.json"
    original = skill_path.read_text(encoding="utf-8")
    try:
        skill_path.write_text(original + "\n", encoding="utf-8")
        after = terminology_snapshot_hash(ROOT)
    finally:
        skill_path.write_text(original, encoding="utf-8")
    assert before != after

from __future__ import annotations

import json
from pathlib import Path

from scripts.harden_skill_inheritance_canon import harden
from scripts.translation_review_common import (
    community_term_matches,
    item_scoped_context_hash,
    load_community_terms,
    load_locked_terms,
    locked_term_matches,
)


def _write(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _seed(tmp_path: Path) -> Path:
    glossary = tmp_path / "glossary"
    _write(
        glossary / "term_registry.json",
        {
            "terms": [
                {"id": "resource.skill_pt", "locked": True, "zh_cn": ["技能点", "技能点数"], "target_vi": "Skill Pt"},
                {"id": "skill.hint", "locked": True, "zh_cn": ["技能灵感", "技能提示"], "target_vi": "Skill Hint"},
                {"id": "legacy.spark", "locked": True, "zh_cn": ["因子"], "target_vi": "Spark"},
            ]
        },
    )
    _write(
        glossary / "ui_community_terms.json",
        {
            "terms": [
                {
                    "id": "common.skill.generic",
                    "source_aliases": ["技能"],
                    "preferred": "Skill",
                    "accepted": ["Skill"],
                    "forbidden": ["Kỹ năng"],
                    "require_accepted": True,
                },
                {
                    "id": "common.skill_points",
                    "source_aliases": ["技能点", "技能点数"],
                    "preferred": "Skill Pt",
                    "accepted": ["Skill Pt"],
                    "forbidden": ["Điểm kỹ năng"],
                    "require_accepted": True,
                },
                {
                    "id": "common.skill_hint",
                    "source_aliases": ["技能灵感", "技能提示"],
                    "preferred": "Skill Hint",
                    "accepted": ["Skill Hint"],
                    "forbidden": ["Gợi ý kỹ năng"],
                    "require_accepted": True,
                },
                {
                    "id": "common.spark",
                    "source_aliases": ["因子"],
                    "preferred": "Spark",
                    "accepted": ["Spark", "Sparks"],
                    "forbidden": ["Nhân tố"],
                    "require_accepted": True,
                },
                {"id": "common.legacy", "source_aliases": [], "preferred": "Legacy", "accepted": ["Legacy"]},
                {"id": "common.guest_legacy", "source_aliases": [], "preferred": "Guest Legacy", "accepted": ["Guest Legacy"]},
                {"id": "common.inspiration", "source_aliases": [], "preferred": "Inspiration", "accepted": ["Inspiration"]},
            ]
        },
    )
    _write(
        glossary / "source_bridge_terms.json",
        {"schema_version": 1, "policy": {}, "terms": [], "untrusted_sources": []},
    )
    harden(tmp_path)
    return tmp_path


def _terms_by_id(terms: list[dict[str, object]]) -> dict[str, dict[str, object]]:
    return {str(term.get("id")): term for term in terms}


def test_skill_pt_system_usage_and_display_variants(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    terms = load_community_terms(root)
    for target in ("Skill Pt", "Skill Pts", "Skill Points"):
        matched = community_term_matches(
            "SingleMode0202",
            "技能点数",
            target,
            terms,
            source_path="localize_dict.json",
            json_path=["SingleMode0202"],
        )
        record = next(item for item in matched if item["id"] == "common.skill_points")
        assert record["accepted_present"] is True
        assert record["forbidden_present"] is False


def test_skill_pt_rejects_legacy_resource_wording_but_not_generic_points(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    terms = load_community_terms(root)
    matched = community_term_matches(
        "SingleMode0207",
        "目前的技能点数",
        "Điểm kỹ năng hiện tại",
        terms,
        source_path="localize_dict.json",
        json_path=["SingleMode0207"],
    )
    record = next(item for item in matched if item["id"] == "common.skill_points")
    assert record["forbidden_present"] is True
    assert record["accepted_present"] is False
    assert community_term_matches(
        None,
        "获得3点评价点",
        "Nhận 3 điểm đánh giá",
        terms,
        source_path="text_data_dict.json",
        json_path=["163", "1"],
    ) == []


def test_skill_hint_full_compound_matches_but_plain_inspiration_does_not(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    terms = load_community_terms(root)
    matched = community_term_matches(
        "SingleMode661023",
        "获得的技能灵感",
        "Skill Hints đã nhận",
        terms,
        source_path="localize_dict.json",
        json_path=["SingleMode661023"],
    )
    assert any(item["id"] == "common.skill_hint" for item in matched)
    assert community_term_matches(
        None,
        "这给了我新的灵感",
        "Điều này cho tôi cảm hứng mới",
        terms,
        source_path="text_data_dict.json",
        json_path=["163", "1"],
    ) == []


def test_hint_lv_is_exact_ui_context_only(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    terms = load_community_terms(root)
    matched = community_term_matches(
        "SingleMode0358",
        "「{0}」的灵感等级已为最大",
        "Hint Lv của 「{0}」 đã đạt tối đa",
        terms,
        source_path="localize_dict.json",
        json_path=["SingleMode0358"],
    )
    assert any(item["id"] == "common.skill_hint.level.singlemode0358" for item in matched)
    assert community_term_matches(
        "Story999",
        "灵感等级越来越高",
        "Mức cảm hứng ngày càng cao",
        terms,
        source_path="localize_dict.json",
        json_path=["Story999"],
    ) == []


def test_spark_matches_inheritance_description_but_not_generic_story_factor(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    terms = load_community_terms(root)
    matched = community_term_matches(
        None,
        "速度因子星级提升",
        "Spark Speed tăng sao",
        terms,
        source_path="text_data_dict.json",
        json_path=["172", "1001"],
    )
    assert any(item["id"] == "common.spark.inheritance_description" for item in matched)
    assert community_term_matches(
        None,
        "失败的主要因子是天气",
        "Yếu tố chính gây thất bại là thời tiết",
        terms,
        source_path="text_data_dict.json",
        json_path=["163", "1001"],
    ) == []


def test_spark_localize_ui_is_scoped_away_from_assets(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    terms = load_community_terms(root)
    matched = community_term_matches(
        "Outgame0341",
        "拥有因子",
        "Sparks sở hữu",
        terms,
        source_path="localize_dict.json",
        json_path=["Outgame0341"],
    )
    assert any(item["id"] == "common.spark.localize_ui" for item in matched)
    assert community_term_matches(
        None,
        "这个因子导致了误会",
        "Yếu tố này gây hiểu lầm",
        terms,
        source_path="storytimeline_01.asset",
        json_path=["story", "1"],
    ) == []


def test_locked_spark_no_longer_globally_matches_generic_factor(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    terms = load_locked_terms(root)
    assert locked_term_matches(
        "失败的主要因子是天气",
        "Yếu tố chính gây thất bại là thời tiết",
        terms,
        source_path="text_data_dict.json",
        json_path=["163", "1"],
    ) == []
    matched = locked_term_matches(
        "力量因子",
        "Power Spark",
        terms,
        source_path="text_data_dict.json",
        json_path=["172", "1"],
    )
    assert any(item["id"] == "legacy.spark.inheritance_description" for item in matched)


def test_affinity_is_locked_only_to_observed_legacy_ui_keys(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    terms = load_community_terms(root)
    for key, source in (("Outgame0343", "相性奖励"), ("Outgame0345", "相性：◎"), ("Outgame0346", "相性：〇"), ("Outgame0347", "相性：△")):
        matched = community_term_matches(
            key,
            source,
            source.replace("相性", "Affinity"),
            terms,
            source_path="localize_dict.json",
            json_path=[key],
        )
        assert any(item["id"] == "common.legacy.affinity.outgame034x" for item in matched)
    assert community_term_matches(
        "StoryAffinity",
        "两个人相性很好",
        "Hai người rất hợp nhau",
        terms,
        source_path="localize_dict.json",
        json_path=["StoryAffinity"],
    ) == []


def test_bare_inheritance_words_are_not_forced_to_legacy_or_inspiration(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    terms = load_community_terms(root)
    ids = _terms_by_id(terms)
    assert ids["common.legacy"].get("source_aliases") == []
    assert ids["common.guest_legacy"].get("source_aliases") == []
    assert ids["common.inspiration"].get("source_aliases") == []
    assert not any(item["id"] in {"common.legacy", "common.guest_legacy", "common.inspiration"} for item in community_term_matches(
        "SingleMode0187",
        "继承",
        "Kế thừa",
        terms,
        source_path="localize_dict.json",
        json_path=["SingleMode0187"],
    ))
    assert community_term_matches(
        None,
        "传承之伟大，未来相连之尊贵",
        "Sự vĩ đại của truyền thừa, sự cao quý nối liền tương lai",
        terms,
        source_path="text_data_dict.json",
        json_path=["163", "1111"],
    ) == []


def test_representative_individual_skill_name_does_not_receive_generic_skill_rule(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    terms = load_community_terms(root)
    matched = community_term_matches(
        None,
        "G00 1st.F∞;",
        "G00 1st.F∞;",
        terms,
        source_path="text_data_dict.json",
        json_path=["47", "102601"],
    )
    assert not any(item["id"] == "common.skill.generic" for item in matched)


def test_scoped_skill_inheritance_rules_have_item_context_only(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    community = load_community_terms(root)
    locked = load_locked_terms(root)
    spark_hash = item_scoped_context_hash(
        key=None,
        source="速度因子",
        source_path="text_data_dict.json",
        json_path=["172", "1"],
        locked_terms=locked,
        community_terms=community,
    )
    prose_hash = item_scoped_context_hash(
        key=None,
        source="失败的主要因子是天气",
        source_path="text_data_dict.json",
        json_path=["163", "1"],
        locked_terms=locked,
        community_terms=community,
    )
    assert spark_hash is not None
    assert prose_hash is None


def test_hardener_is_idempotent_and_does_not_add_bridge_substring_rules(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    paths = [
        root / "glossary/term_registry.json",
        root / "glossary/ui_community_terms.json",
        root / "glossary/source_bridge_terms.json",
    ]
    before = [path.read_text(encoding="utf-8") for path in paths]
    harden(root)
    after = [path.read_text(encoding="utf-8") for path in paths]
    assert after == before

    bridge = json.loads((root / "glossary/source_bridge_terms.json").read_text(encoding="utf-8"))
    aliases = {
        alias
        for term in bridge.get("terms", [])
        for alias in term.get("zh_cn", [])
    }
    assert "提示" not in aliases
    assert "灵感" not in aliases
    assert "继承" not in aliases
    assert "传承" not in aliases

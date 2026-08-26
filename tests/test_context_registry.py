from __future__ import annotations

from hachimi_tl_vi.context_registry import (
    compact_character_registry,
    compact_observed_term_memory,
    compact_speech_bible,
    select_relevant_characters,
    select_relevant_terms,
)
from hachimi_tl_vi.model import SourceEntry


def entry(text: str) -> SourceEntry:
    return SourceEntry(uid="zhcn:test", kind="text_data", source_text=text, locator={})


def test_character_alias_selects_only_relevant_character():
    registry = {
        "schema_version": 3,
        "characters": {
            "1068": {
                "game_id": 1068,
                "canonical": "Kitasan Black",
                "ja": ["キタサンブラック"],
                "zh_cn": ["北部玄驹"],
            },
            "1001": {
                "game_id": 1001,
                "canonical": "Special Week",
                "ja": ["スペシャルウィーク"],
                "zh_cn": ["特别周"],
            },
        },
    }
    selected = select_relevant_characters([entry("北部玄驹今天也要训练！")], registry)
    assert list(selected) == ["1068"]
    assert selected["1068"]["canonical"] == "Kitasan Black"


def test_energy_is_selected_without_confusing_stamina():
    registry = {
        "terms": [
            {"id": "stat.stamina", "zh_cn": ["耐力"], "target_vi": "Thể lực"},
            {"id": "resource.energy", "zh_cn": ["体力"], "target_vi": "Năng lượng"},
        ]
    }
    selected = select_relevant_terms([entry("体力恢复了30")], registry, include_core=False)
    assert [item["id"] for item in selected] == ["resource.energy"]


def test_context_fields_can_select_character():
    registry = {
        "characters": {
            "1007": {
                "canonical": "Gold Ship",
                "ja": ["ゴールドシップ"],
                "zh_cn": ["黄金船"],
            }
        }
    }
    source = SourceEntry(
        uid="zhcn:test",
        kind="story",
        source_text="走吧！",
        locator={},
        context={"speaker": "黄金船"},
    )
    compact = compact_character_registry([source], registry)
    assert compact["characters"]["1007"]["canonical"] == "Gold Ship"


def test_speech_bible_uses_selected_character_ids():
    source = SourceEntry(
        uid="zhcn:test",
        kind="story",
        source_text="走吧！",
        locator={},
        context={"speaker": "黄金船"},
    )
    selected_characters = {
        "1007": {
            "canonical": "Gold Ship",
            "zh_cn": ["黄金船"],
        }
    }
    bible = {
        "schema_version": 1,
        "policy": {"pronouns": "contextual"},
        "profiles": {
            "1007": {"canonical": "Gold Ship", "register": ["hỗn loạn"]},
            "1001": {"canonical": "Special Week", "register": ["chân thành"]},
        },
    }
    compact = compact_speech_bible([source], bible, selected_characters)
    assert list(compact["profiles"]) == ["1007"]
    assert compact["profiles"]["1007"]["register"] == ["hỗn loạn"]


def test_observed_memory_injects_only_exactly_relevant_entities():
    observed = {
        "schema_version": 1,
        "policy": {"priority": "locked wins"},
        "terms": [
            {"id": "observed:1", "zh_cn": ["弧线教授"], "target_vi": "Giáo sư Đường cong"},
            {"id": "observed:2", "zh_cn": ["日本德比"], "target_vi": "Japan Derby"},
        ],
    }
    compact = compact_observed_term_memory([entry("获得技能：弧线教授")], observed)
    assert [term["id"] for term in compact["terms"]] == ["observed:1"]
    assert compact["terms"][0]["target_vi"] == "Giáo sư Đường cong"

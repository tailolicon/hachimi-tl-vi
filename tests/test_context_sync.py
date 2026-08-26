from __future__ import annotations

from scripts.extract_context_candidates import extract
from scripts.sync_context_registry import build_registry


def test_character_sync_joins_by_game_id_and_preserves_manual_rules():
    progress = {
        "source_repo": "example/source",
        "source_commit": "abc123",
        "source_language": "zh-CN",
    }
    uma_data = {
        "generatedAt": "2026-07-25T00:00:00Z",
        "characters": [
            {
                "gameId": 1068,
                "nameEn": "Kitasan Black",
                "nameJp": "キタサンブラック",
                "nameInternal": "kitasanblack",
                "preferredUrl": "kitasan-black",
            },
            {
                "gameId": 1001,
                "nameEn": "Special Week",
                "nameJp": "スペシャルウィーク",
            },
        ],
    }
    source = {"6": {"1068": "北部玄驹", "1001": "特别周", "9001": "骏川手纲"}}
    existing = {
        "default_rules": ["rule"],
        "characters": {
            "old-kitasan-key": {
                "canonical": "Kitasan Black",
                "ja": ["キタサンブラック"],
                "zh_cn": ["北部玄驹"],
                "speech_rules": ["Giọng sáng, năng động."],
                "relationships": {"trainer": "tin cậy"},
            }
        },
    }

    result = build_registry(progress, uma_data, source, existing)
    assert result["characters"]["1068"]["canonical"] == "Kitasan Black"
    assert result["characters"]["1068"]["zh_cn"] == ["北部玄驹"]
    assert result["characters"]["1068"]["speech_rules"] == ["Giọng sáng, năng động."]
    assert result["characters"]["1068"]["relationships"] == {"trainer": "tin cậy"}
    assert result["characters"]["1068"]["identity_status"] == "verified_game_id"
    assert result["unresolved_source_characters"] == {"9001": "骏川手纲"}


def test_null_game_ids_are_represented_without_guessing_and_verified_override_can_join():
    progress = {
        "source_repo": "example/source",
        "source_commit": "abc123",
        "source_language": "zh-CN",
    }
    uma_data = {
        "generatedAt": "2026-07-25T00:00:00Z",
        "characters": [
            {
                "gameId": None,
                "nameEn": "Titleholder",
                "nameJp": "タイトルホルダー",
                "nameInternal": "titleholder",
            },
            {
                "gameId": None,
                "nameEn": "Samson Big",
                "nameJp": "サムソンビッグ",
                "nameInternal": "samsonbig",
            },
        ],
    }
    source = {"6": {"1148": "领衔", "9999": "未知角色"}}

    result = build_registry(progress, uma_data, source, {})
    assert result["characters"]["1148"]["canonical"] == "Titleholder"
    assert result["characters"]["1148"]["zh_cn"] == ["领衔"]
    assert result["characters"]["1148"]["identity_status"] == "verified_game_id_override"
    assert result["characters"]["slug:samsonbig"]["canonical"] == "Samson Big"
    assert result["characters"]["slug:samsonbig"]["identity_status"] == "structured_without_game_id"
    assert "game_id" not in result["characters"]["slug:samsonbig"]
    assert result["generated"]["structured_count"] == 2
    assert result["generated"]["resolved_game_id_count"] == 1
    assert result["generated"]["structured_without_game_id_count"] == 1
    assert result["generated"]["zh_alias_matches"] == 1
    assert result["unresolved_source_characters"] == {"9999": "未知角色"}


def test_candidate_extractor_uses_known_text_data_categories_and_scenarios():
    source = {
        "6": {"1001": "特别周"},
        "32": {"1": "日本德比"},
        "47": {"200331": "弧线教授"},
        "75": {"1": "[测试]支援卡"},
        "999": {"1": "育成剧本「新设！URA总决赛！！」通关后解锁"},
    }
    candidates, counts = extract(source)
    kinds = {item["kind"] for item in candidates}
    assert "character_name" in kinds
    assert "race_name" in kinds
    assert "skill_name" in kinds
    assert "support_card_full_name" in kinds
    assert "scenario_name" in kinds
    assert counts["skill_name"] == 1

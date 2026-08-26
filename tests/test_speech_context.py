from __future__ import annotations

import json
from pathlib import Path

from scripts.build_speech_review_queue import build_queue
from scripts.extract_speaker_samples import build_samples


def test_speaker_samples_map_aliases_and_keep_unmatched(tmp_path: Path):
    upstream = tmp_path / "upstream"
    story = upstream / "localized_data/assets/story/data/00/0001"
    story.mkdir(parents=True)
    (story / "storytimeline_test.json").write_text(
        json.dumps(
            {
                "text_block_list": [
                    {"name": "黄金船", "text": "哈哈！今天也来点有趣的吧！"},
                    {"name": "特别周", "text": "我会努力的！"},
                    {"name": "训练员", "text": "那就开始吧。"},
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    characters = {
        "characters": {
            "1007": {"canonical": "Gold Ship", "zh_cn": ["黄金船"]},
            "1001": {"canonical": "Special Week", "zh_cn": ["特别周"]},
        }
    }

    result = build_samples(upstream, characters, "abc123", max_samples=4)
    assert result["stats"]["dialogue_blocks"] == 3
    assert result["stats"]["matched_blocks"] == 2
    assert set(result["characters"]) == {"1007", "1001"}
    assert result["characters"]["1007"]["dialogue_count"] == 1
    assert result["characters"]["1007"]["samples"][0]["speaker"] == "黄金船"
    assert result["unmatched_speakers"][0]["speaker"] == "训练员"


def test_speech_review_queue_prioritizes_uncovered_sampled_character():
    characters = {
        "characters": {
            "1007": {"game_id": 1007, "canonical": "Gold Ship", "zh_cn": ["黄金船"]},
            "1001": {"game_id": 1001, "canonical": "Special Week", "zh_cn": ["特别周"]},
        }
    }
    bible = {
        "profiles": {
            "1007": {"canonical": "Gold Ship", "status": "curated_official_profile"}
        }
    }
    samples = {
        "source_commit": "abc123",
        "characters": {
            "1007": {"dialogue_count": 10, "signals": {}, "source_speakers": ["黄金船"], "samples": []},
            "1001": {"dialogue_count": 50, "signals": {}, "source_speakers": ["特别周"], "samples": []},
        },
        "unmatched_speakers": [{"speaker": "训练员", "dialogue_count": 20}],
    }

    queue = build_queue(characters, bible, samples)
    assert queue["summary"]["covered_profiles"] == 1
    assert queue["summary"]["needs_review"] == 1
    assert queue["characters"][0]["character_key"] == "1001"
    assert queue["characters"][0]["status"] == "needs_review"
    assert queue["unmatched_speakers"][0]["status"] == "needs_identity_review"

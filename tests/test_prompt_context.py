from __future__ import annotations

import json
from pathlib import Path

from hachimi_tl_vi.model import SourceEntry
from hachimi_tl_vi.translators.prompt import build_messages, infer_source_language


def test_infer_zhcn_from_uid():
    entry = SourceEntry(uid="zhcn:test", kind="text_data", source_text="速度", locator={})
    assert infer_source_language(entry) == "zh-CN"


def test_prompt_loads_shared_game_context(tmp_path: Path):
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    (glossary / "game_context.json").write_text(json.dumps({"game": "Uma Musume Pretty Derby"}), encoding="utf-8")
    (glossary / "term_registry.json").write_text(json.dumps({"terms": [{"zh_cn": ["速度"], "target_vi": "Tốc độ", "locked": True}]}), encoding="utf-8")
    (glossary / "terminology.json").write_text("{}", encoding="utf-8")
    (glossary / "characters.json").write_text("{}", encoding="utf-8")
    (glossary / "style_rules.json").write_text("{}", encoding="utf-8")

    entry = SourceEntry(uid="zhcn:test", kind="text_data", source_text="速度", locator={})
    messages = build_messages([entry], glossary)
    assert "Uma Musume Pretty Derby" in messages[0]["content"]
    payload = json.loads(messages[1]["content"])
    assert payload["source_languages"] == ["zh-CN"]
    assert payload["game_context"]["game"] == "Uma Musume Pretty Derby"
    assert payload["term_registry"]["terms"][0]["target_vi"] == "Tốc độ"
    assert payload["items"][0]["source_language"] == "zh-CN"

from __future__ import annotations

import json
from pathlib import Path

from hachimi_tl_vi.model import SourceEntry
from hachimi_tl_vi.translators.prompt import build_messages, compact_translation_regressions


def test_compacts_only_relevant_regressions() -> None:
    entries = [SourceEntry(uid="zhcn:a", kind="localize", source_text="重新启动", locator={})]
    memory = {
        "policy": {"hard_block": "test"},
        "entries": [
            {
                "id": "r1",
                "uid": "zhcn:a",
                "source_text": "重新启动",
                "rejected_targets": ["Khởi chạy lại"],
                "approved_target": "Khởi động lại",
            },
            {
                "id": "r2",
                "uid": "zhcn:b",
                "source_text": "别的文本",
                "rejected_targets": ["Sai"],
                "approved_target": "Đúng",
            },
        ],
    }
    compact = compact_translation_regressions(entries, memory)
    assert [item["id"] for item in compact["entries"]] == ["r1"]


def test_build_messages_injects_regression_memory(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    defaults = {
        "terminology.json": {},
        "term_registry.json": {},
        "ui_community_terms.json": {},
        "source_bridge_terms.json": {},
        "source_bridge_risks.generated.json": {},
        "skill_name_style.json": {},
        "observed_terms.json": {},
        "characters.json": {},
        "speech_bible.json": {},
        "speech_evidence.json": {},
        "style_rules.json": {},
        "game_context.json": {},
    }
    for name, payload in defaults.items():
        (glossary / name).write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    (glossary / "translation_regressions.generated.json").write_text(
        json.dumps(
            {
                "policy": {"hard_block": "never reuse rejected target"},
                "entries": [
                    {
                        "id": "r1",
                        "uid": "zhcn:a",
                        "source_text": "重新启动",
                        "rejected_targets": ["Khởi chạy lại"],
                        "approved_target": "Khởi động lại",
                    }
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    entry = SourceEntry(uid="zhcn:a", kind="localize", source_text="重新启动", locator={})
    messages = build_messages([entry], glossary)
    payload = json.loads(messages[1]["content"])
    assert payload["translation_regressions"]["entries"][0]["rejected_targets"] == ["Khởi chạy lại"]
    assert payload["translation_regressions"]["entries"][0]["approved_target"] == "Khởi động lại"
    assert "translation_regressions" in messages[0]["content"]
    assert "TUYỆT ĐỐI không tái sử dụng" in messages[0]["content"]

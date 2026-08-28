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


def _write_default_glossary(glossary: Path) -> None:
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


def test_build_messages_injects_regression_memory(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    _write_default_glossary(glossary)
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
                        "origins": ["translation_review"],
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


def test_build_messages_injects_ui_regression_evidence(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    _write_default_glossary(glossary)
    (glossary / "translation_regressions.generated.json").write_text(
        json.dumps(
            {
                "policy": {
                    "hard_block": "never reuse rejected target",
                    "ui_memory": "UI revisions preserve layout/control evidence",
                },
                "entries": [
                    {
                        "id": "ui-r1",
                        "uid": "zhcn:menu",
                        "source_text": "物品/转换",
                        "rejected_targets": ["Vật phẩm/Chuyển đổi"],
                        "approved_target": "Vật phẩm / Đổi",
                        "origins": ["ui_review"],
                        "ui_contexts": [
                            {
                                "key": "Menu424001",
                                "control_type": "menu_tile",
                                "risk_flags": ["overflow_risk", "verbose_wording"],
                            }
                        ],
                    }
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    entry = SourceEntry(uid="zhcn:menu", kind="localize", source_text="物品/转换", locator={})
    messages = build_messages([entry], glossary)
    regression = json.loads(messages[1]["content"])["translation_regressions"]
    assert regression["policy"]["ui_memory"] == "UI revisions preserve layout/control evidence"
    assert regression["entries"][0]["origins"] == ["ui_review"]
    assert regression["entries"][0]["ui_contexts"][0]["key"] == "Menu424001"
    assert regression["entries"][0]["ui_contexts"][0]["control_type"] == "menu_tile"
    assert regression["entries"][0]["rejected_targets"] == ["Vật phẩm/Chuyển đổi"]

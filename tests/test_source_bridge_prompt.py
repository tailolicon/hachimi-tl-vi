from __future__ import annotations

import json
from pathlib import Path

from hachimi_tl_vi.model import SourceEntry
from hachimi_tl_vi.translators.prompt import build_messages, compact_source_bridge_rules


def _config() -> dict:
    return {
        "policy": {"purpose": "test"},
        "terms": [
            {
                "id": "currency.monies",
                "zh_cn": ["金币"],
                "accepted": ["Monies"],
                "forbidden": ["xu"],
            },
            {
                "id": "resource.cleat",
                "zh_cn": ["蹄铁"],
                "accepted": ["Cleat", "Cleats"],
                "forbidden": ["móng ngựa"],
            },
        ],
        "untrusted_sources": [
            {
                "id": "bridge.skill.frontline_target",
                "zh_cn_exact": ["前行"],
                "ja": ["前列狙い"],
                "mode": "defer_until_canonical",
            }
        ],
    }


def test_compacts_source_bridge_rules_per_batch() -> None:
    entries = [
        SourceEntry(uid="zhcn:money", kind="localize", source_text="金币不足", locator={}),
        SourceEntry(uid="zhcn:front", kind="localize", source_text="前行", locator={}),
    ]
    compact = compact_source_bridge_rules(entries, _config())
    assert [item["id"] for item in compact["terms"]] == ["currency.monies"]
    assert [item["id"] for item in compact["untrusted_sources"]] == ["bridge.skill.frontline_target"]


def test_japanese_source_does_not_receive_zhcn_bridge_rules() -> None:
    entries = [SourceEntry(uid="ja:test", kind="localize", source_text="マニー", locator={})]
    compact = compact_source_bridge_rules(entries, _config())
    assert compact["terms"] == []
    assert compact["untrusted_sources"] == []


def test_build_messages_injects_relevant_bridge_terminology(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    for name, payload in {
        "terminology.json": {},
        "term_registry.json": {},
        "ui_community_terms.json": {},
        "skill_name_style.json": {},
        "observed_terms.json": {},
        "characters.json": {},
        "speech_bible.json": {},
        "speech_evidence.json": {},
        "style_rules.json": {},
        "game_context.json": {},
        "source_bridge_terms.json": _config(),
    }.items():
        (glossary / name).write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    entry = SourceEntry(uid="zhcn:money", kind="localize", source_text="金币不足", locator={})
    messages = build_messages([entry], glossary)
    payload = json.loads(messages[1]["content"])
    bridge = payload["source_bridge_terminology"]
    assert bridge["terms"][0]["id"] == "currency.monies"
    assert bridge["terms"][0]["accepted"] == ["Monies"]
    assert "source_bridge_terminology" in messages[0]["content"]
    assert "金币 -> Monies" in messages[0]["content"]

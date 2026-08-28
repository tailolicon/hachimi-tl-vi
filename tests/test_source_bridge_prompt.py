from __future__ import annotations

import json
from pathlib import Path

from hachimi_tl_vi.model import SourceEntry
from hachimi_tl_vi.translators.prompt import (
    build_messages,
    compact_source_bridge_rules,
    merge_source_bridge_configs,
)


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


def _generated() -> dict:
    return {
        "summary": {"untrusted_source_count": 1},
        "untrusted_sources": [
            {
                "id": "curation.bridge.example",
                "zh_cn_exact": ["一线曙光"],
                "mode": "defer_until_canonical",
                "evidence": [
                    {
                        "path": "work/curation/results/term-0008/claim.json",
                        "note": "The zh-CN title changes the image relative to JP.",
                    }
                ],
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


def test_generated_risks_merge_with_manual_rules_and_manual_wins_duplicates() -> None:
    generated = _generated()
    generated["untrusted_sources"].append(
        {
            "id": "generated.duplicate",
            "zh_cn_exact": ["前行"],
            "mode": "defer_until_canonical",
        }
    )

    merged = merge_source_bridge_configs(_config(), generated)

    assert [item["id"] for item in merged["untrusted_sources"]] == [
        "bridge.skill.frontline_target",
        "curation.bridge.example",
    ]
    assert merged["generated_summary"]["untrusted_source_count"] == 1


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
        "source_bridge_risks.generated.json": _generated(),
    }.items():
        (glossary / name).write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    money = SourceEntry(uid="zhcn:money", kind="localize", source_text="金币不足", locator={})
    messages = build_messages([money], glossary)
    payload = json.loads(messages[1]["content"])
    bridge = payload["source_bridge_terminology"]
    assert bridge["terms"][0]["id"] == "currency.monies"
    assert bridge["terms"][0]["accepted"] == ["Monies"]
    assert bridge["untrusted_sources"] == []
    assert "source_bridge_terminology" in messages[0]["content"]
    assert "金币 -> Monies" in messages[0]["content"]

    lossy = SourceEntry(uid="zhcn:lossy", kind="skill_name", source_text="一线曙光", locator={})
    messages = build_messages([lossy], glossary)
    payload = json.loads(messages[1]["content"])
    risks = payload["source_bridge_terminology"]["untrusted_sources"]
    assert [item["id"] for item in risks] == ["curation.bridge.example"]
    assert risks[0]["evidence"][0]["path"].startswith("work/curation/results/")

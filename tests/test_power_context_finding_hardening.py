from __future__ import annotations

import json
from pathlib import Path

from scripts.harden_power_context_finding import TERM_ID, harden
from scripts.resolve_context_guard_findings import POWER_CONTEXT_GUARD_IDS, resolve
from scripts.translation_review_common import community_term_matches, load_community_terms


def _write_terms(root: Path) -> None:
    glossary = root / "glossary"
    glossary.mkdir(parents=True)
    (glossary / "ui_community_terms.json").write_text(
        json.dumps(
            {
                "terms": [
                    {
                        "id": TERM_ID,
                        "category": "stat",
                        "source_aliases": ["パワー", "力量"],
                        "preferred": "Power",
                        "accepted": ["Power"],
                        "forbidden": ["Sức mạnh"],
                        "require_accepted": True,
                    }
                ]
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def test_power_context_hardening_preserves_stat_and_excludes_narrative(tmp_path: Path) -> None:
    _write_terms(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    terms = load_community_terms(tmp_path)
    stat = community_term_matches(
        None,
        "力量",
        "Sức mạnh",
        terms,
        source_path="text_data_dict.json",
        json_path=["172", "1"],
    )
    strong_power = community_term_matches(
        None,
        "拥有强大力量的人",
        "Người sở hữu sức mạnh lớn",
        terms,
        source_path="localize_dict.json",
        json_path=["StoryPower"],
    )
    narrative_title = community_term_matches(
        None,
        "商品的力量",
        "Sức mạnh của hàng hóa",
        terms,
        source_path="text_data_dict.json",
        json_path=["130", "181"],
    )
    narrative_item = community_term_matches(
        None,
        "具有激发不可思议力量的能力。",
        "Có khả năng khơi dậy sức mạnh kỳ diệu.",
        terms,
        source_path="text_data_dict.json",
        json_path=["10", "110"],
    )
    physical_strength = community_term_matches(
        None,
        "有着能够依靠尾巴来支撑自己的力量……据说",
        "Nghe nói có sức mạnh đủ để dùng đuôi chống đỡ cả cơ thể……",
        terms,
        source_path="text_data_dict.json",
        json_path=["167", "1026"],
    )
    assert stat[0]["id"] == TERM_ID
    assert stat[0]["preferred"] == "Power"
    assert strong_power == []
    assert narrative_title == []
    assert narrative_item == []
    assert physical_strength == []


def test_regenerated_power_context_ids_resolve_only_after_matcher_is_neutralized(tmp_path: Path) -> None:
    _write_terms(tmp_path)
    assert harden(tmp_path) is True
    findings = [
        {
            "finding_id": "cf-df66d1828a60839c",
            "status": "open",
            "source_zh_cn": "商品的力量",
            "canonical_resolution": None,
            "evidence": [{
                "source_path": "text_data_dict.json",
                "json_path": ["130", "181"],
                "source_text": "商品的力量",
                "current_text": "Sức mạnh của hàng hóa",
            }],
        },
        {
            "finding_id": "cf-1606ab03065110f0",
            "status": "open",
            "source_zh_cn": "强大力量",
            "canonical_resolution": None,
            "evidence": [{
                "source_path": "localize_dict.json",
                "json_path": ["StoryPower"],
                "source_text": "拥有强大力量的人",
                "current_text": "Người sở hữu sức mạnh lớn",
            }],
        },
        {
            "finding_id": "cf-1fb0ec7c1c77dfb1",
            "status": "open",
            "source_zh_cn": "精神力量",
            "canonical_resolution": None,
            "evidence": [{
                "source_path": "text_data_dict.json",
                "json_path": ["128", "1"],
                "source_text": "精神力量",
                "current_text": "Sức mạnh tinh thần",
            }],
        },
    ]
    (tmp_path / "glossary" / "canonical_findings.json").write_text(
        json.dumps({"schema_version": 1, "findings": findings}, ensure_ascii=False),
        encoding="utf-8",
    )

    assert resolve(tmp_path) is True
    payload = json.loads((tmp_path / "glossary" / "canonical_findings.json").read_text(encoding="utf-8"))
    by_id = {row["finding_id"]: row for row in payload["findings"]}
    for finding_id in {"cf-df66d1828a60839c", "cf-1606ab03065110f0"}:
        assert finding_id in POWER_CONTEXT_GUARD_IDS
        assert by_id[finding_id]["canonical_resolution"] == {
            "layer": "context_guard",
            "term_id": TERM_ID,
            "target_vi": "Power",
        }
    assert "cf-1fb0ec7c1c77dfb1" not in POWER_CONTEXT_GUARD_IDS
    assert by_id["cf-1fb0ec7c1c77dfb1"]["canonical_resolution"] is None

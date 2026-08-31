from __future__ import annotations

import json
from pathlib import Path

from scripts.resolve_context_guard_findings import resolve
from scripts.translation_review_common import community_term_matches, load_community_terms


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _seed(tmp_path: Path) -> None:
    _write(tmp_path / "glossary" / "ui_community_terms.json", {"terms": [{
        "id": "common.stat.power",
        "source_aliases": ["力量"],
        "preferred": "Power",
        "accepted": ["Power"],
        "forbidden": ["Sức mạnh"],
        "require_accepted": True,
        "exclude_source_contains": [
            "商品的力量",
            "不可思议力量",
            "超越极限力量",
            "莱茵力量",
        ],
    }]})
    _write(tmp_path / "glossary" / "term_registry.json", {"terms": []})
    _write(tmp_path / "glossary" / "canonical_findings.json", {"findings": [
        {
            "finding_id": "cf-ecde28dd625ae647",
            "status": "open",
            "source_zh_cn": "力量",
            "canonical_resolution": None,
            "review_resolution": None,
            "evidence": [
                {
                    "source_path": "text_data_dict.json",
                    "json_path": ["10", "110"],
                    "source_text": "具有激发不可思议力量的能力。\\n可用于支援卡的强化。",
                    "current_text": "Có khả năng khơi dậy sức mạnh kỳ diệu.\\nCó thể dùng để nâng cấp Support Card.",
                },
                {
                    "source_path": "text_data_dict.json",
                    "json_path": ["10", "144"],
                    "source_text": "据说是可以激发出超越极限力量的\\n彩虹色力量石。",
                    "current_text": "Viên đá sức mạnh cầu vồng được cho là có thể khơi dậy sức mạnh vượt giới hạn.",
                },
            ],
        },
        {
            "finding_id": "cf-5204eca8a2e00ad5",
            "status": "open",
            "source_zh_cn": "莱茵力量的特殊服装",
            "canonical_resolution": None,
            "review_resolution": None,
            "evidence": [
                {
                    "source_path": "text_data_dict.json",
                    "json_path": ["15", "110901"],
                    "source_text": "莱茵力量的特殊服装",
                    "current_text": "Trang phục đặc biệt (Rhein Kraft)",
                },
                {
                    "source_path": "text_data_dict.json",
                    "json_path": ["15", "110902"],
                    "source_text": "莱茵力量的特殊服装",
                    "current_text": "Trang phục đặc biệt (Rhein Kraft)",
                },
            ],
        },
    ]})


def test_narrative_and_proper_name_power_findings_resolve_without_disabling_power_stat(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert resolve(tmp_path) is True
    assert resolve(tmp_path) is False

    payload = json.loads((tmp_path / "glossary" / "canonical_findings.json").read_text(encoding="utf-8"))
    for finding in payload["findings"]:
        assert finding["canonical_resolution"] == {
            "layer": "context_guard",
            "term_id": "common.stat.power",
            "target_vi": "Power",
        }

    terms = load_community_terms(tmp_path)
    narrative = community_term_matches(
        None,
        "具有激发不可思议力量的能力。",
        "Có khả năng khơi dậy sức mạnh kỳ diệu.",
        terms,
        source_path="text_data_dict.json",
        json_path=["10", "110"],
    )
    assert not any(match["id"] == "common.stat.power" for match in narrative)

    proper_name = community_term_matches(
        None,
        "莱茵力量的特殊服装",
        "Trang phục đặc biệt (Rhein Kraft)",
        terms,
        source_path="text_data_dict.json",
        json_path=["15", "110901"],
    )
    assert not any(match["id"] == "common.stat.power" for match in proper_name)

    stat = community_term_matches(
        None,
        "力量达到1200以上",
        "Power đạt từ 1200 trở lên",
        terms,
        source_path="text_data_dict.json",
        json_path=["131", "999"],
    )
    power = next(match for match in stat if match["id"] == "common.stat.power")
    assert power["accepted_present"] is True
    assert power["forbidden_present"] is False

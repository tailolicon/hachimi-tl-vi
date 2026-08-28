from __future__ import annotations

import json
from pathlib import Path

from hachimi_tl_vi.translation_guard import TranslationQualityGuard
from scripts.translation_review_common import community_term_matches, source_bridge_term_matches


PRIMARY = {
    "id": "common.condition.night_owl",
    "source_aliases": ["熬夜"],
    "preferred": "Night Owl",
    "accepted": ["Night Owl"],
    "compact": [],
    "forbidden": ["Thức khuya"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [["142"]],
    "match_mode": "exact",
}

REFERENCE = {
    "id": "common.condition.night_owl.reference",
    "source_aliases": ["「熬夜」", "“熬夜”", "『熬夜』", '"熬夜"'],
    "preferred": "Night Owl",
    "accepted": ["Night Owl"],
    "compact": [],
    "forbidden": ["Thức khuya"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "match_mode": "contains",
}

BRIDGE_REFERENCE = {
    "id": "condition.night_owl.reference",
    "zh_cn": ["「熬夜」", "“熬夜”", "『熬夜』", '"熬夜"'],
    "preferred": "Night Owl",
    "accepted": ["Night Owl"],
    "forbidden": ["Thức khuya"],
    "require_accepted": True,
    "match_mode": "contains",
}


def test_condition_label_and_quoted_reference_are_distinct_contexts() -> None:
    label = community_term_matches(
        None,
        "熬夜",
        "Thức khuya",
        [PRIMARY, REFERENCE],
        source_path="text_data_dict.json",
        json_path=["142", "1"],
    )
    assert [item["id"] for item in label] == ["common.condition.night_owl"]

    ordinary = community_term_matches(
        None,
        "今天熬夜了",
        "Hôm nay đã thức khuya",
        [PRIMARY, REFERENCE],
        source_path="text_data_dict.json",
        json_path=["143", "1"],
    )
    assert ordinary == []

    quoted = community_term_matches(
        None,
        "休息7回以上且未持有过「熬夜」状态",
        "Nghỉ ít nhất 7 lần và chưa từng có trạng thái Thức khuya",
        [PRIMARY, REFERENCE],
        source_path="text_data_dict.json",
        json_path=["131", "283"],
    )
    assert [item["id"] for item in quoted] == ["common.condition.night_owl.reference"]
    assert quoted[0]["forbidden_present"] is True
    assert quoted[0]["accepted_present"] is False


def test_source_bridge_only_matches_explicitly_quoted_reference() -> None:
    assert source_bridge_term_matches(
        "今天熬夜了",
        "Hôm nay đã thức khuya",
        [BRIDGE_REFERENCE],
        source_path="text_data_dict.json",
        json_path=["143", "1"],
    ) == []
    matched = source_bridge_term_matches(
        "未持有过「熬夜」状态",
        "Chưa từng có trạng thái Thức khuya",
        [BRIDGE_REFERENCE],
        source_path="text_data_dict.json",
        json_path=["131", "283"],
    )
    assert matched[0]["id"] == "condition.night_owl.reference"


def test_translation_guard_enforces_quoted_reference_without_touching_prose(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    (glossary / "term_registry.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "ui_community_terms.json").write_text(
        json.dumps({"terms": [PRIMARY, REFERENCE]}, ensure_ascii=False),
        encoding="utf-8",
    )
    guard = TranslationQualityGuard(glossary)

    errors = guard.validate(
        "未持有过「熬夜」状态",
        "Chưa từng có trạng thái Thức khuya",
        source_path="text_data_dict.json",
        json_path=["131", "283"],
    )
    assert "community_forbidden:common.condition.night_owl.reference" in errors
    assert "community_required:common.condition.night_owl.reference" in errors
    assert guard.validate(
        "未持有过「熬夜」状态",
        "Chưa từng có trạng thái Night Owl",
        source_path="text_data_dict.json",
        json_path=["131", "283"],
    ) == []
    assert guard.validate(
        "今天熬夜了",
        "Hôm nay đã thức khuya",
        source_path="text_data_dict.json",
        json_path=["143", "1"],
    ) == []

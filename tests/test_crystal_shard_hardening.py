from __future__ import annotations

import json
from pathlib import Path

from scripts.harden_crystal_shard_canon import harden
from scripts.translation_review_common import source_bridge_term_matches


def _terms(tmp_path: Path) -> list[dict]:
    path = tmp_path / "glossary" / "source_bridge_terms.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps({"schema_version": 1, "terms": []}) + "\n", encoding="utf-8")
    harden(tmp_path)
    return json.loads(path.read_text(encoding="utf-8"))["terms"]


def test_crystal_shard_shop_labels_are_canonical_and_exact_scoped(tmp_path: Path) -> None:
    terms = _terms(tmp_path)
    cases = [
        ("Shop420161", "结晶片兑换", "Crystal Shard Exchange", "resource.crystal_shard"),
        ("Shop420162", "彩虹结晶片", "Rainbow Crystal Shards", "resource.crystal_shard.rainbow"),
        ("Shop420163", "金色结晶片", "Gold Crystal Shards", "resource.crystal_shard.gold"),
    ]
    for key, source, target, expected_id in cases:
        matches = source_bridge_term_matches(source, target, terms, key=key, source_path="localize_dict.json", json_path=[key])
        assert [item["id"] for item in matches] == [expected_id]
        assert matches[0]["accepted_present"] is True


def test_crystal_shard_calques_are_rejected_without_overmatching(tmp_path: Path) -> None:
    terms = _terms(tmp_path)
    bad = source_bridge_term_matches("彩虹结晶片", "Mảnh kết tinh Cầu vồng", terms, key="Shop420162", source_path="localize_dict.json", json_path=["Shop420162"])
    other = source_bridge_term_matches("彩虹结晶片", "Mảnh kết tinh Cầu vồng", terms, key="StoryEvent9999996", source_path="localize_dict.json", json_path=["StoryEvent9999996"])
    assert [item["id"] for item in bad] == ["resource.crystal_shard.rainbow"]
    assert bad[0]["forbidden_present"] is True
    assert other == []


def test_crystal_shard_hardener_is_idempotent(tmp_path: Path) -> None:
    _terms(tmp_path)
    path = tmp_path / "glossary" / "source_bridge_terms.json"
    first = path.read_bytes()
    harden(tmp_path)
    assert path.read_bytes() == first

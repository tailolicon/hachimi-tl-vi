from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import refresh_canonical_resolutions
from scripts.harden_unfading_cattleya_finding import DECISION, TERM, harden


def _seed(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    for name, payload in [
        ("ui_community_terms.json", {"schema_version": 1, "terms": []}),
        ("terminology_reviews.json", {"schema_version": 1, "decisions": []}),
        ("source_bridge_terms.json", {"terms": []}),
        ("term_registry.json", {"terms": []}),
    ]:
        (glossary / name).write_text(json.dumps(payload), encoding="utf-8")


def _finding() -> dict:
    return {
        "finding_id": "cf-177daab93abe2ad4",
        "status": "open",
        "source_zh_cn": "永不凋零的Cattleya",
        "match_mode": "contains",
        "source_paths": ["text_data_dict.json"],
        "key_exact": [],
        "json_path_prefixes": [],
        "suggested_targets_vi": [],
        "canonical_resolution": None,
        "review_resolution": None,
    }


def test_unfading_cattleya_hardener_resolves_finding(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False
    community = json.loads((tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8"))
    rule = next(item for item in community["terms"] if item["id"] == TERM["id"])
    assert rule["preferred"] == "Cattleya Bất Tàn"
    reviews = json.loads((tmp_path / "glossary" / "terminology_reviews.json").read_text(encoding="utf-8"))
    decision = next(item for item in reviews["decisions"] if item["decision_id"] == DECISION["decision_id"])
    assert decision["ja"] == ["不凋なるCattleya"]
    finding = refresh_canonical_resolutions(tmp_path, {"schema_version": 1, "findings": [_finding()]})["findings"][0]
    assert finding["canonical_resolution"] == {
        "layer": "community",
        "term_id": "skill.gentildonna.unfading_cattleya",
        "target_vi": "Cattleya Bất Tàn",
    }

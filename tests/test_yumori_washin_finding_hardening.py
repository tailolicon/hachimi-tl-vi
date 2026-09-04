from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import refresh_canonical_resolutions
from scripts.harden_yumori_washin_finding import DECISION, TERM, harden


def _seed(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    (glossary / "ui_community_terms.json").write_text(json.dumps({"schema_version": 1, "terms": []}), encoding="utf-8")
    (glossary / "terminology_reviews.json").write_text(json.dumps({"schema_version": 1, "decisions": []}), encoding="utf-8")
    (glossary / "source_bridge_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "term_registry.json").write_text(json.dumps({"terms": []}), encoding="utf-8")


def _finding(*, source_text: str = "汤守的和心") -> dict:
    return {
        "finding_id": "cf-141e1dbe5b4bc506",
        "status": "open",
        "source_zh_cn": "汤守的和心",
        "match_mode": "contains",
        "source_paths": ["text_data_dict.json"],
        "key_exact": [],
        "json_path_prefixes": [],
        "suggested_targets_vi": [],
        "canonical_resolution": None,
        "review_resolution": None,
        "evidence": [{"source_path": "text_data_dict.json", "source_text": source_text}],
    }


def test_hardener_resolves_jp_only_unique_skill(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    community = json.loads((tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8"))
    rule = next(item for item in community["terms"] if item["id"] == TERM["id"])
    assert rule["preferred"] == "Tấm Lòng Người Giữ Suối Nóng"
    assert rule["match_mode"] == "contains"

    reviews = json.loads((tmp_path / "glossary" / "terminology_reviews.json").read_text(encoding="utf-8"))
    decision = next(item for item in reviews["decisions"] if item["decision_id"] == DECISION["decision_id"])
    assert decision["ja"] == ["湯守の和心"]

    finding = refresh_canonical_resolutions(tmp_path, {"schema_version": 1, "findings": [_finding()]})["findings"][0]
    assert finding["canonical_resolution"] == {
        "layer": "community",
        "term_id": "skill.wonder_acute.yumori_washin",
        "target_vi": "Tấm Lòng Người Giữ Suối Nóng",
    }


def test_contains_rule_resolves_factor_sentence(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    finding = refresh_canonical_resolutions(
        tmp_path,
        {"schema_version": 1, "findings": [_finding(source_text="可获得「汤守的和心」技能灵感的因子")]},
    )["findings"][0]
    assert finding["canonical_resolution"] is not None

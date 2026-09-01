from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import refresh_canonical_resolutions
from scripts.harden_ichibanboshi_song_finding import ICHIBANBOSHI, ICHIBANBOSHI_DECISION, harden


def _seed(tmp_path: Path, *, finding_prefixes: list[list[str]] | None = None, evidence_category: str = "16") -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    (glossary / "ui_community_terms.json").write_text(json.dumps({"schema_version": 1, "terms": []}), encoding="utf-8")
    (glossary / "terminology_reviews.json").write_text(json.dumps({"schema_version": 1, "decisions": []}), encoding="utf-8")
    (glossary / "term_registry.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "source_bridge_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "canonical_findings.json").write_text(json.dumps({"schema_version": 1, "findings": [{
        "finding_id": "cf-027a0f62d9583a5f", "status": "open", "source_zh_cn": "イチバン星が駆ける空",
        "match_mode": "exact", "source_paths": ["text_data_dict.json"], "key_exact": [],
        "json_path_prefixes": finding_prefixes or [], "suggested_targets_vi": [],
        "canonical_resolution": None, "review_resolution": None,
        "evidence": [{
            "source_path": "text_data_dict.json",
            "json_path": [evidence_category, "1099"],
            "source_text": "イチバン星が駆ける空",
        }],
    }]}), encoding="utf-8")


def test_ichibanboshi_repairs_scope_and_resolves_song_title_table(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    community = json.loads((tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8"))
    rule = next(item for item in community["terms"] if item["id"] == ICHIBANBOSHI["id"])
    assert rule["preferred"] == "Ichibanboshi ga Kakeru Sora"
    assert rule["json_path_prefixes"] == [["16"]]
    assert rule["match_mode"] == "exact"

    reviews = json.loads((tmp_path / "glossary" / "terminology_reviews.json").read_text(encoding="utf-8"))
    decision = next(item for item in reviews["decisions"] if item["decision_id"] == ICHIBANBOSHI_DECISION["decision_id"])
    assert decision["target_vi"] == "Ichibanboshi ga Kakeru Sora"

    ledger = json.loads((tmp_path / "glossary" / "canonical_findings.json").read_text(encoding="utf-8"))
    assert ledger["findings"][0]["json_path_prefixes"] == [["16"]]
    finding = refresh_canonical_resolutions(tmp_path, ledger)["findings"][0]
    assert finding["review_resolution"]["target_vi"] == "Ichibanboshi ga Kakeru Sora"
    assert finding["canonical_resolution"] == {
        "layer": "community",
        "term_id": "song.ichibanboshi_ga_kakeru_sora",
        "target_vi": "Ichibanboshi ga Kakeru Sora",
    }


def test_ichibanboshi_does_not_repair_or_resolve_outside_song_table(tmp_path: Path) -> None:
    _seed(tmp_path, evidence_category="163")
    assert harden(tmp_path) is True
    ledger = json.loads((tmp_path / "glossary" / "canonical_findings.json").read_text(encoding="utf-8"))
    assert ledger["findings"][0]["json_path_prefixes"] == []
    finding = refresh_canonical_resolutions(tmp_path, ledger)["findings"][0]
    assert finding["canonical_resolution"] is None

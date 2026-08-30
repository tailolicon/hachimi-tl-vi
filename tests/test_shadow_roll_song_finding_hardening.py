from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import refresh_canonical_resolutions
from scripts.harden_shadow_roll_song_finding import SHADOW_ROLL, SHADOW_ROLL_DECISION, harden


def _seed(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    (glossary / "ui_community_terms.json").write_text(json.dumps({"schema_version": 1, "terms": []}), encoding="utf-8")
    (glossary / "terminology_reviews.json").write_text(json.dumps({"schema_version": 1, "decisions": []}), encoding="utf-8")
    (glossary / "term_registry.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "source_bridge_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")


def test_shadow_roll_resolves_song_title_table(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False
    community = json.loads((tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8"))
    rule = next(item for item in community["terms"] if item["id"] == SHADOW_ROLL["id"])
    assert rule["preferred"] == "Shadow Roll no Chikai (The Solid Revision)"
    assert rule["json_path_prefixes"] == [["16"]]
    reviews = json.loads((tmp_path / "glossary" / "terminology_reviews.json").read_text(encoding="utf-8"))
    decision = next(item for item in reviews["decisions"] if item["decision_id"] == SHADOW_ROLL_DECISION["decision_id"])
    assert decision["target_vi"] == "Shadow Roll no Chikai (The Solid Revision)"
    ledger = {"schema_version": 1, "findings": [{
        "finding_id": "cf-test-shadow-roll", "status": "open", "source_zh_cn": "シャドーロールの誓い（The Solid Revision）",
        "match_mode": "exact", "source_paths": ["text_data_dict.json"], "key_exact": [],
        "json_path_prefixes": [["16"]], "suggested_targets_vi": [],
        "canonical_resolution": None, "review_resolution": None,
    }]}
    finding = refresh_canonical_resolutions(tmp_path, ledger)["findings"][0]
    assert finding["review_resolution"]["target_vi"] == "Shadow Roll no Chikai (The Solid Revision)"
    assert finding["canonical_resolution"] == {"layer": "community", "term_id": "song.shadow_roll_no_chikai_the_solid_revision", "target_vi": "Shadow Roll no Chikai (The Solid Revision)"}


def test_shadow_roll_does_not_resolve_outside_song_table(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    ledger = {"schema_version": 1, "findings": [{
        "finding_id": "cf-test-shadow-roll-wrong", "status": "open", "source_zh_cn": "シャドーロールの誓い（The Solid Revision）",
        "match_mode": "exact", "source_paths": ["text_data_dict.json"], "key_exact": [],
        "json_path_prefixes": [["163"]], "suggested_targets_vi": [],
        "canonical_resolution": None, "review_resolution": None,
    }]}
    assert refresh_canonical_resolutions(tmp_path, ledger)["findings"][0]["canonical_resolution"] is None

from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import refresh_canonical_resolutions
from scripts.harden_training_rank_finding import TRAINING_RANK, TRAINING_RANK_DECISION, harden


def _seed(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    (glossary / "ui_community_terms.json").write_text(json.dumps({"schema_version": 1, "terms": []}), encoding="utf-8")
    (glossary / "terminology_reviews.json").write_text(json.dumps({"schema_version": 1, "decisions": []}), encoding="utf-8")
    (glossary / "term_registry.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "source_bridge_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")


def test_training_rank_resolves_room_match_restriction(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False
    community = json.loads((tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8"))
    rule = next(item for item in community["terms"] if item["id"] == TRAINING_RANK["id"])
    assert rule["preferred"] == "Training Rank"
    assert rule["source_paths"] == ["localize_dict.json"]
    assert rule["key_exact"] == ["RoomMatch0047"]
    assert rule["match_mode"] == "contains"
    reviews = json.loads((tmp_path / "glossary" / "terminology_reviews.json").read_text(encoding="utf-8"))
    decision = next(item for item in reviews["decisions"] if item["decision_id"] == TRAINING_RANK_DECISION["decision_id"])
    assert decision["target_vi"] == "Training Rank"
    ledger = {"schema_version": 1, "findings": [{
        "finding_id": "cf-test-training-rank", "status": "open", "source_zh_cn": "育成等级",
        "match_mode": "contains", "source_paths": ["localize_dict.json"], "key_exact": ["RoomMatch0047"],
        "json_path_prefixes": [], "suggested_targets_vi": [], "canonical_resolution": None, "review_resolution": None,
    }]}
    finding = refresh_canonical_resolutions(tmp_path, ledger)["findings"][0]
    assert finding["review_resolution"]["target_vi"] == "Training Rank"
    assert finding["canonical_resolution"] == {"layer": "community", "term_id": "system.training_rank", "target_vi": "Training Rank"}


def test_training_rank_does_not_resolve_other_keys(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    ledger = {"schema_version": 1, "findings": [{
        "finding_id": "cf-test-training-rank-wrong", "status": "open", "source_zh_cn": "育成等级",
        "match_mode": "contains", "source_paths": ["localize_dict.json"], "key_exact": ["OtherKey"],
        "json_path_prefixes": [], "suggested_targets_vi": [], "canonical_resolution": None, "review_resolution": None,
    }]}
    assert refresh_canonical_resolutions(tmp_path, ledger)["findings"][0]["canonical_resolution"] is None

from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import active_findings, refresh_canonical_resolutions
from scripts.harden_hip_hip_victory_song_finding import (
    HIP_HIP_VICTORY,
    HIP_HIP_VICTORY_DECISION,
    TARGET,
    harden,
)
from scripts.translation_review_common import community_term_matches


def _seed(tmp_path: Path, *, finding_prefixes: list[list[str]] | None = None, evidence_category: str = "16") -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    (glossary / "ui_community_terms.json").write_text(json.dumps({"schema_version": 1, "terms": []}), encoding="utf-8")
    (glossary / "terminology_reviews.json").write_text(json.dumps({"schema_version": 1, "decisions": []}), encoding="utf-8")
    (glossary / "term_registry.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "source_bridge_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "canonical_findings.json").write_text(json.dumps({"schema_version": 1, "findings": [{
        "finding_id": "cf-09acdcebbe013cfd", "status": "open", "source_zh_cn": "どどっと優勝！大感謝祭！！！",
        "match_mode": "exact", "source_paths": ["text_data_dict.json"], "key_exact": [],
        "json_path_prefixes": finding_prefixes or [], "suggested_targets_vi": [],
        "canonical_resolution": None, "review_resolution": None,
        "evidence": [{
            "source_path": "text_data_dict.json",
            "json_path": [evidence_category, "1085"],
            "source_text": "どどっと優勝！大感謝祭！！！",
        }],
    }]}), encoding="utf-8")


def test_hip_hip_victory_repairs_scope_and_resolves_official_song_title(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    community = json.loads((tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8"))
    rule = next(item for item in community["terms"] if item["id"] == HIP_HIP_VICTORY["id"])
    assert rule["preferred"] == TARGET
    assert rule["json_path_prefixes"] == [["16"]]
    assert rule["match_mode"] == "exact"

    exact = community_term_matches(
        None,
        "どどっと優勝！大感謝祭！！！",
        TARGET,
        community["terms"],
        source_path="text_data_dict.json",
        json_path=["16", "1085"],
    )
    assert [item["id"] for item in exact if item["id"] == HIP_HIP_VICTORY["id"]] == [HIP_HIP_VICTORY["id"]]
    longer = community_term_matches(
        None,
        "今日はどどっと優勝！大感謝祭！！！を聴こう",
        TARGET,
        community["terms"],
        source_path="text_data_dict.json",
        json_path=["16", "1085"],
    )
    assert all(item["id"] != HIP_HIP_VICTORY["id"] for item in longer)

    reviews = json.loads((tmp_path / "glossary" / "terminology_reviews.json").read_text(encoding="utf-8"))
    decision = next(item for item in reviews["decisions"] if item["decision_id"] == HIP_HIP_VICTORY_DECISION["decision_id"])
    assert decision["target_vi"] == TARGET

    ledger = json.loads((tmp_path / "glossary" / "canonical_findings.json").read_text(encoding="utf-8"))
    assert ledger["findings"][0]["json_path_prefixes"] == [["16"]]
    refreshed = refresh_canonical_resolutions(tmp_path, ledger)
    finding = refreshed["findings"][0]
    assert finding["review_resolution"]["target_vi"] == TARGET
    assert finding["canonical_resolution"] == {
        "layer": "community",
        "term_id": HIP_HIP_VICTORY["id"],
        "target_vi": TARGET,
    }
    assert active_findings(refreshed) == []


def test_hip_hip_victory_does_not_repair_or_resolve_outside_song_table(tmp_path: Path) -> None:
    _seed(tmp_path, evidence_category="163")
    assert harden(tmp_path) is True
    ledger = json.loads((tmp_path / "glossary" / "canonical_findings.json").read_text(encoding="utf-8"))
    assert ledger["findings"][0]["json_path_prefixes"] == []
    finding = refresh_canonical_resolutions(tmp_path, ledger)["findings"][0]
    assert finding["canonical_resolution"] is None

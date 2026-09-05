from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import active_findings, refresh_canonical_resolutions
from scripts.harden_brightness_omen_context_finding import DECISION, EXCLUSIONS, FINDING_ID, TERM_ID, harden


def _seed(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    (glossary / "term_registry.json").write_text(json.dumps({
        "terms": [{
            "id": TERM_ID,
            "category": "skill_name",
            "zh_cn": ["光明"],
            "target_vi": "Ánh sáng",
            "locked": True,
            "match_mode": "contains",
        }]
    }, ensure_ascii=False), encoding="utf-8")
    (glossary / "terminology_reviews.json").write_text(
        json.dumps({"schema_version": 1, "decisions": []}, ensure_ascii=False), encoding="utf-8"
    )
    (glossary / "ui_community_terms.json").write_text(json.dumps({"schema_version": 1, "terms": []}), encoding="utf-8")
    (glossary / "source_bridge_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")


def test_hardener_adds_narrow_exclusions_and_ignore_decision(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    registry = json.loads((tmp_path / "glossary" / "term_registry.json").read_text(encoding="utf-8"))
    term = registry["terms"][0]
    assert term["exclude_source_contains"] == EXCLUSIONS
    reviews = json.loads((tmp_path / "glossary" / "terminology_reviews.json").read_text(encoding="utf-8"))
    assert reviews["decisions"] == [DECISION]


def test_ignore_resolution_stops_only_context_finding_from_blocking(tmp_path: Path) -> None:
    _seed(tmp_path)
    harden(tmp_path)
    ledger = {"schema_version": 1, "findings": [{
        "finding_id": FINDING_ID,
        "status": "open",
        "source_zh_cn": "光明的征兆",
        "match_mode": "exact",
        "source_paths": ["text_data_dict.json"],
        "key_exact": [],
        "json_path_prefixes": [],
        "suggested_targets_vi": [],
        "canonical_resolution": None,
        "review_resolution": None,
    }]}
    refreshed = refresh_canonical_resolutions(tmp_path, ledger)
    finding = refreshed["findings"][0]
    assert finding["canonical_resolution"] is None
    assert finding["review_resolution"]["decision_id"] == DECISION["decision_id"]
    assert finding["review_resolution"]["action"] == "ignore"
    assert active_findings(refreshed) == []

from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import active_findings, refresh_canonical_resolutions
from scripts.harden_rushed_prose_finding import DECISION_ID, FINDING_ID, SOURCE, harden


def _seed(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir(parents=True)
    (glossary / "terminology_reviews.json").write_text(
        json.dumps({"schema_version": 1, "decisions": []}, ensure_ascii=False), encoding="utf-8"
    )
    (glossary / "ui_community_terms.json").write_text(json.dumps({"schema_version": 1, "terms": []}), encoding="utf-8")
    (glossary / "term_registry.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "source_bridge_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "skill_name_style.json").write_text(json.dumps({"canonical_examples": []}), encoding="utf-8")
    finding = {
        "finding_id": FINDING_ID,
        "status": "open",
        "source_zh_cn": SOURCE,
        "match_mode": "exact",
        "source_paths": ["text_data_dict.json"],
        "key_exact": [],
        "json_path_prefixes": [["128"]],
        "suggested_targets_vi": [],
        "canonical_resolution": None,
        "review_resolution": None,
    }
    (glossary / "canonical_findings.json").write_text(
        json.dumps({"schema_version": 1, "findings": [finding]}, ensure_ascii=False), encoding="utf-8"
    )


def test_rushed_prose_ignore_is_exact_scoped_and_idempotent(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    reviews = json.loads((tmp_path / "glossary" / "terminology_reviews.json").read_text(encoding="utf-8"))
    decision = next(item for item in reviews["decisions"] if item["decision_id"] == DECISION_ID)
    assert decision["action"] == "ignore"
    assert decision["source_zh_cn"] == SOURCE
    assert decision["source_paths"] == ["text_data_dict.json"]
    assert decision["json_path_prefixes"] == [["128", "1105"]]
    assert decision["match_mode"] == "exact"
    assert decision["invalidation_scope"] == "item"

    ledger = json.loads((tmp_path / "glossary" / "canonical_findings.json").read_text(encoding="utf-8"))
    refreshed = refresh_canonical_resolutions(tmp_path, ledger)
    finding = refreshed["findings"][0]
    assert finding["canonical_resolution"] is None
    assert finding["review_resolution"] == {
        "decision_id": DECISION_ID,
        "action": "ignore",
        "target_vi": None,
    }
    assert active_findings(refreshed) == []


def test_exact_ignore_does_not_cover_other_rushed_prose(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    other = {
        "finding_id": "cf-other-rushed-prose",
        "status": "open",
        "source_zh_cn": "焦躁仍然持续着。",
        "match_mode": "exact",
        "source_paths": ["text_data_dict.json"],
        "key_exact": [],
        "json_path_prefixes": [["128", "1105"]],
        "suggested_targets_vi": [],
        "canonical_resolution": None,
        "review_resolution": None,
    }
    refreshed = refresh_canonical_resolutions(tmp_path, {"schema_version": 1, "findings": [other]})
    assert refreshed["findings"][0]["review_resolution"] is None
    assert len(active_findings(refreshed)) == 1

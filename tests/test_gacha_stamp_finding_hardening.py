from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import refresh_canonical_resolutions
from scripts.harden_gacha_stamp_finding import STAMP_DECISION, STAMP_TERM, harden


def _seed(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    (glossary / "ui_community_terms.json").write_text(
        json.dumps({"schema_version": 1, "terms": []}), encoding="utf-8"
    )
    (glossary / "terminology_reviews.json").write_text(
        json.dumps({"schema_version": 1, "decisions": []}), encoding="utf-8"
    )
    (glossary / "term_registry.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "source_bridge_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "canonical_findings.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "findings": [
                    {
                        "finding_id": "cf-74133ec3607b9e34",
                        "status": "open",
                        "source_zh_cn": "印章",
                        "match_mode": "contains",
                        "source_paths": ["localize_dict.json"],
                        "key_exact": [],
                        "json_path_prefixes": [],
                        "suggested_targets_vi": [],
                        "canonical_resolution": None,
                        "review_resolution": None,
                        "evidence": [
                            {
                                "source_path": "localize_dict.json",
                                "json_path": ["Gacha408002"],
                                "source_text": "获得印章！",
                                "current_text": "Đã nhận Stamp!",
                            }
                        ],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )


def test_gacha_stamp_hardener_is_idempotent_and_resolves_finding(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    community = json.loads((tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8"))
    rule = next(item for item in community["terms"] if item["id"] == STAMP_TERM["id"])
    assert rule["preferred"] == "Stamp"
    assert rule["source_paths"] == ["localize_dict.json"]
    assert rule["match_mode"] == "contains"

    reviews = json.loads((tmp_path / "glossary" / "terminology_reviews.json").read_text(encoding="utf-8"))
    decision = next(item for item in reviews["decisions"] if item["decision_id"] == STAMP_DECISION["decision_id"])
    assert decision["target_vi"] == "Stamp"

    ledger = json.loads((tmp_path / "glossary" / "canonical_findings.json").read_text(encoding="utf-8"))
    finding = refresh_canonical_resolutions(tmp_path, ledger)["findings"][0]
    assert finding["review_resolution"]["target_vi"] == "Stamp"
    assert finding["canonical_resolution"] == {
        "layer": "community",
        "term_id": "system.gacha_stamp",
        "target_vi": "Stamp",
    }


def test_gacha_stamp_rule_does_not_cover_other_source_paths(tmp_path: Path) -> None:
    _seed(tmp_path)
    ledger_path = tmp_path / "glossary" / "canonical_findings.json"
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    ledger["findings"][0]["source_paths"] = ["text_data_dict.json"]
    ledger_path.write_text(json.dumps(ledger), encoding="utf-8")

    assert harden(tmp_path) is True
    finding = refresh_canonical_resolutions(tmp_path, ledger)["findings"][0]
    assert finding["canonical_resolution"] is None

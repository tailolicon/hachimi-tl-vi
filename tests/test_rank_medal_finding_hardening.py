from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import active_findings, refresh_canonical_resolutions
from scripts.harden_rank_medal_finding import OLD_DECISION_ID, RANK_MEDAL_IGNORE, harden


def _seed(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    (glossary / "ui_community_terms.json").write_text(json.dumps({"schema_version": 1, "terms": []}), encoding="utf-8")
    (glossary / "terminology_reviews.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "decisions": [
                    {
                        "decision_id": OLD_DECISION_ID,
                        "source_zh_cn": "等级奖牌",
                        "action": "defer",
                        "target_vi": "",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    (glossary / "term_registry.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "source_bridge_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")


def test_rank_medal_ignore_is_exact_idempotent_and_nonblocking(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    reviews = json.loads((tmp_path / "glossary" / "terminology_reviews.json").read_text(encoding="utf-8"))
    assert all(item.get("decision_id") != OLD_DECISION_ID for item in reviews["decisions"])
    decision = next(item for item in reviews["decisions"] if item["decision_id"] == RANK_MEDAL_IGNORE["decision_id"])
    assert decision["source_zh_cn"] == "等级奖牌"
    assert decision["action"] == "ignore"
    assert decision["target_vi"] == ""
    assert decision["invalidation_scope"] == "item"
    assert decision["source_paths"] == ["text_data_dict.json"]
    assert decision["json_path_prefixes"] == [["133", "3"]]
    assert decision["match_mode"] == "exact"

    ledger = {
        "schema_version": 1,
        "findings": [
            {
                "finding_id": "cf-test-rank-medal",
                "status": "open",
                "source_zh_cn": "等级奖牌",
                "match_mode": "exact",
                "source_paths": ["text_data_dict.json"],
                "key_exact": ["3"],
                "json_path_prefixes": [["133", "3"]],
                "suggested_targets_vi": ["Huy chương cấp"],
                "canonical_resolution": None,
                "review_resolution": None,
            }
        ],
    }
    finding = refresh_canonical_resolutions(tmp_path, ledger)["findings"][0]
    assert finding["review_resolution"]["decision_id"] == RANK_MEDAL_IGNORE["decision_id"]
    assert finding["review_resolution"]["action"] == "ignore"
    assert finding["canonical_resolution"] is None
    assert active_findings([finding]) == []

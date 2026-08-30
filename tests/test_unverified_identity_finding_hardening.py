from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import refresh_canonical_resolutions
from scripts.harden_unverified_identity_finding import DEFERRED_IDENTITIES, harden


def _seed(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    (glossary / "ui_community_terms.json").write_text(json.dumps({"schema_version": 1, "terms": []}), encoding="utf-8")
    (glossary / "terminology_reviews.json").write_text(json.dumps({"schema_version": 1, "decisions": []}), encoding="utf-8")
    (glossary / "term_registry.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "source_bridge_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")


def test_unverified_identity_defers_are_idempotent() -> None:
    assert {item["source_zh_cn"] for item in DEFERRED_IDENTITIES} == {"スタホTV", "热血誓言", "英雄的光辉", "待春之蕾"}
    assert all(item["action"] == "defer" and item["target_vi"] == "" for item in DEFERRED_IDENTITIES)


def test_unverified_identity_defers_remain_blocking(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False
    reviews = json.loads((tmp_path / "glossary" / "terminology_reviews.json").read_text(encoding="utf-8"))
    assert len(reviews["decisions"]) == len(DEFERRED_IDENTITIES)

    for index, record in enumerate(DEFERRED_IDENTITIES):
        ledger = {"schema_version": 1, "findings": [{
            "finding_id": f"cf-test-defer-{index}", "status": "open", "source_zh_cn": record["source_zh_cn"],
            "match_mode": "exact", "source_paths": ["text_data_dict.json"], "key_exact": [],
            "json_path_prefixes": [], "suggested_targets_vi": [],
            "canonical_resolution": None, "review_resolution": None,
        }]}
        finding = refresh_canonical_resolutions(tmp_path, ledger)["findings"][0]
        assert finding["review_resolution"]["action"] == "defer"
        assert finding["canonical_resolution"] is None

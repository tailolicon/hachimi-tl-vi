from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import refresh_canonical_resolutions
from scripts.harden_mecha_system_finding import MECHA_TERMS, harden


def _seed(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    (glossary / "ui_community_terms.json").write_text(json.dumps({"schema_version": 1, "terms": []}), encoding="utf-8")
    (glossary / "terminology_reviews.json").write_text(json.dumps({"schema_version": 1, "decisions": []}), encoding="utf-8")
    (glossary / "term_registry.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "source_bridge_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")


def _finding(source: str, prefix: str = "131") -> dict:
    return {
        "finding_id": f"cf-test-{source}",
        "status": "open",
        "source_zh_cn": source,
        "match_mode": "contains",
        "source_paths": ["text_data_dict.json"],
        "key_exact": [],
        "json_path_prefixes": [[prefix]],
        "suggested_targets_vi": [],
        "canonical_resolution": None,
        "review_resolution": None,
    }


def test_mecha_system_findings_resolve_and_hardener_is_idempotent(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False
    for spec in MECHA_TERMS:
        resolved = refresh_canonical_resolutions(
            tmp_path,
            {"schema_version": 1, "findings": [_finding(spec["source"])]},
        )["findings"][0]
        assert resolved["review_resolution"]["target_vi"] == spec["target"]
        assert resolved["canonical_resolution"] == {
            "layer": "community",
            "term_id": spec["id"],
            "target_vi": spec["target"],
        }


def test_mecha_system_rules_do_not_escape_category_131(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    spec = MECHA_TERMS[0]
    resolved = refresh_canonical_resolutions(
        tmp_path,
        {"schema_version": 1, "findings": [_finding(spec["source"], "147")]},
    )["findings"][0]
    assert resolved["canonical_resolution"] is None

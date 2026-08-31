from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import refresh_canonical_resolutions
from scripts.harden_uaf_discipline_finding import DISCIPLINES, harden


def _seed(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    (glossary / "ui_community_terms.json").write_text(json.dumps({"schema_version": 1, "terms": []}), encoding="utf-8")
    (glossary / "terminology_reviews.json").write_text(json.dumps({"schema_version": 1, "decisions": []}), encoding="utf-8")
    (glossary / "term_registry.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "source_bridge_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")


def _finding(source: str, source_path: str = "localize_dict.json") -> dict:
    return {
        "finding_id": f"cf-test-{source}",
        "status": "open",
        "source_zh_cn": source,
        "match_mode": "exact",
        "source_paths": [source_path],
        "key_exact": [],
        "json_path_prefixes": [],
        "suggested_targets_vi": [],
        "canonical_resolution": None,
        "review_resolution": None,
    }


def test_all_uaf_discipline_findings_resolve_and_hardener_is_idempotent(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False
    for source, target, slug in DISCIPLINES:
        resolved = refresh_canonical_resolutions(
            tmp_path,
            {"schema_version": 1, "findings": [_finding(source)]},
        )["findings"][0]
        assert resolved["review_resolution"]["target_vi"] == target
        assert resolved["canonical_resolution"] == {
            "layer": "community",
            "term_id": f"scenario.uaf.discipline.{slug}",
            "target_vi": target,
        }


def test_uaf_discipline_rules_are_localize_scoped(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    source, _, _ = DISCIPLINES[0]
    resolved = refresh_canonical_resolutions(
        tmp_path,
        {"schema_version": 1, "findings": [_finding(source, "text_data_dict.json")]},
    )["findings"][0]
    assert resolved["canonical_resolution"] is None

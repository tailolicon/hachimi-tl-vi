from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import active_findings, refresh_canonical_resolutions
from scripts.harden_turf_surface_context_finding import (
    BASE_RULE_ID,
    FINDING_ID,
    SOURCE_ZH,
    TARGET,
    ZH_RULE_ID,
    harden,
)


def _finding(source: str = SOURCE_ZH) -> dict:
    return {
        "finding_id": FINDING_ID,
        "status": "open",
        "source_zh_cn": source,
        "match_mode": "contains",
        "source_paths": ["text_data_dict.json"],
        "key_exact": [],
        "json_path_prefixes": [],
        "suggested_targets_vi": [],
        "canonical_resolution": None,
        "review_resolution": None,
    }


def _seed(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    (glossary / "ui_community_terms.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "terms": [
                    {
                        "id": BASE_RULE_ID,
                        "category": "race_surface",
                        "source_aliases": ["芝", SOURCE_ZH],
                        "preferred": TARGET,
                        "compact": [],
                        "accepted": [TARGET],
                        "forbidden": ["Sân cỏ"],
                        "require_accepted": True,
                        "basis": "Common EN-version surface label.",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    (glossary / "terminology_reviews.json").write_text(
        json.dumps({"schema_version": 1, "decisions": []}), encoding="utf-8"
    )
    (glossary / "canonical_findings.json").write_text(
        json.dumps({"schema_version": 1, "findings": [_finding()]}), encoding="utf-8"
    )
    (glossary / "term_registry.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "source_bridge_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "skill_name_style.json").write_text(
        json.dumps({"canonical_examples": []}), encoding="utf-8"
    )


def test_hardener_splits_zhcn_alias_and_resolves_finding(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    community = json.loads(
        (tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8")
    )
    base = next(item for item in community["terms"] if item["id"] == BASE_RULE_ID)
    zh = next(item for item in community["terms"] if item["id"] == ZH_RULE_ID)
    assert base["source_aliases"] == ["芝"]
    assert zh["source_aliases"] == [SOURCE_ZH]
    assert zh["preferred"] == TARGET
    assert zh["match_mode"] == "exact"

    ledger = json.loads(
        (tmp_path / "glossary" / "canonical_findings.json").read_text(encoding="utf-8")
    )
    resolved_ledger = refresh_canonical_resolutions(tmp_path, ledger)
    resolved = resolved_ledger["findings"][0]
    assert resolved["suggested_targets_vi"] == [TARGET]
    assert resolved["canonical_resolution"] == {
        "layer": "community",
        "term_id": ZH_RULE_ID,
        "target_vi": TARGET,
    }
    assert resolved["review_resolution"] == {
        "decision_id": "audit.finding.turf-surface-zhcn-context",
        "action": "lock",
        "target_vi": TARGET,
    }
    assert active_findings(resolved_ledger) == []


def test_narrative_grass_prose_does_not_match_exact_turf_rule(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True

    prose = _finding("草地上的花随风摇曳")
    prose["suggested_targets_vi"] = [TARGET]
    resolved = refresh_canonical_resolutions(
        tmp_path, {"schema_version": 1, "findings": [prose]}
    )["findings"][0]
    assert resolved["canonical_resolution"] is None
    assert resolved["review_resolution"] is None

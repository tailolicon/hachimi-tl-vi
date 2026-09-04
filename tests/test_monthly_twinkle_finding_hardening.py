from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import active_findings, refresh_canonical_resolutions
from scripts.harden_monthly_twinkle_finding import (
    DECISION,
    FINDING_IDS,
    KEYS,
    RULE,
    SOURCE_ZH,
    TARGET,
    harden,
)


def _finding(finding_id: str, key: str) -> dict:
    return {
        "finding_id": finding_id,
        "status": "open",
        "source_zh_cn": SOURCE_ZH,
        "match_mode": "contains",
        "source_paths": ["localize_dict.json"],
        "key_exact": [key],
        "json_path_prefixes": [],
        "suggested_targets_vi": [],
        "canonical_resolution": None,
        "review_resolution": None,
    }


def _seed(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    (glossary / "ui_community_terms.json").write_text(
        json.dumps({"schema_version": 1, "terms": []}), encoding="utf-8"
    )
    (glossary / "terminology_reviews.json").write_text(
        json.dumps({"schema_version": 1, "decisions": []}), encoding="utf-8"
    )
    findings = [_finding(fid, key) for fid, key in zip(sorted(FINDING_IDS), KEYS)]
    (glossary / "canonical_findings.json").write_text(
        json.dumps({"schema_version": 1, "findings": findings}), encoding="utf-8"
    )
    (glossary / "term_registry.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "source_bridge_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "skill_name_style.json").write_text(
        json.dumps({"canonical_examples": []}), encoding="utf-8"
    )


def test_hardener_resolves_both_monthly_twinkle_findings_and_is_idempotent(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    community = json.loads(
        (tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8")
    )
    rule = next(item for item in community["terms"] if item["id"] == RULE["id"])
    assert rule["preferred"] == TARGET
    assert rule["match_mode"] == "contains"
    assert rule["source_paths"] == ["localize_dict.json"]
    assert set(rule["key_exact"]) == set(KEYS)

    reviews = json.loads(
        (tmp_path / "glossary" / "terminology_reviews.json").read_text(encoding="utf-8")
    )
    decision = next(
        item for item in reviews["decisions"] if item["decision_id"] == DECISION["decision_id"]
    )
    assert decision["target_vi"] == TARGET
    assert set(decision["key_exact"]) == set(KEYS)

    ledger = json.loads(
        (tmp_path / "glossary" / "canonical_findings.json").read_text(encoding="utf-8")
    )
    resolved_ledger = refresh_canonical_resolutions(tmp_path, ledger)
    for finding in resolved_ledger["findings"]:
        assert finding["suggested_targets_vi"] == [TARGET]
        assert finding["canonical_resolution"] == {
            "layer": "community",
            "term_id": "publication.monthly_twinkle",
            "target_vi": TARGET,
        }
        assert finding["review_resolution"] == {
            "decision_id": "audit.finding.publication-monthly-twinkle",
            "action": "lock",
            "target_vi": TARGET,
        }
    assert active_findings(resolved_ledger) == []


def test_community_rule_is_key_scoped_while_review_lock_recognizes_same_source_identity(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True

    outside = _finding("cf-outside", "OtherKey")
    outside["suggested_targets_vi"] = [TARGET]
    resolved = refresh_canonical_resolutions(
        tmp_path, {"schema_version": 1, "findings": [outside]}
    )["findings"][0]
    assert resolved["canonical_resolution"] is None
    assert resolved["review_resolution"] == {
        "decision_id": "audit.finding.publication-monthly-twinkle",
        "action": "lock",
        "target_vi": TARGET,
    }

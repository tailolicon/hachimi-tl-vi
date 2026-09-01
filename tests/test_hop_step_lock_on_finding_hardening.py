from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import refresh_canonical_resolutions
from scripts.harden_hop_step_lock_on_finding import RULE, TARGET, harden


def _seed(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    (glossary / "ui_community_terms.json").write_text(json.dumps({"schema_version": 1, "terms": []}), encoding="utf-8")
    (glossary / "terminology_reviews.json").write_text(json.dumps({"schema_version": 1, "decisions": []}), encoding="utf-8")
    (glossary / "canonical_findings.json").write_text(json.dumps({"schema_version": 1, "findings": [{"finding_id": "cf-02344f54e2b5da15", "suggested_targets_vi": []}]}), encoding="utf-8")
    (glossary / "term_registry.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "source_bridge_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")


def _finding(source: str = "跃动舞步♪锁定！", prefix: str = "147") -> dict:
    return {
        "finding_id": "cf-test-hop-step-lock-on",
        "status": "open",
        "source_zh_cn": source,
        "match_mode": "exact",
        "source_paths": ["text_data_dict.json"],
        "key_exact": [],
        "json_path_prefixes": [[prefix]],
        "suggested_targets_vi": [],
        "canonical_resolution": None,
        "review_resolution": None,
    }


def test_hardener_resolves_exact_skill_title_and_is_idempotent(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    community = json.loads((tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8"))
    rule = next(item for item in community["terms"] if item["id"] == RULE["id"])
    assert rule["preferred"] == TARGET
    assert rule["match_mode"] == "exact"
    assert rule["json_path_prefixes"] == [["147"]]

    resolved = refresh_canonical_resolutions(tmp_path, {"schema_version": 1, "findings": [_finding()]})["findings"][0]
    assert resolved["canonical_resolution"] == {
        "layer": "community",
        "term_id": "skill.hop_step_lock_on",
        "target_vi": TARGET,
    }
    assert resolved["review_resolution"]["target_vi"] == TARGET


def test_rule_does_not_overmatch_other_text_or_category(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True

    longer = refresh_canonical_resolutions(tmp_path, {"schema_version": 1, "findings": [_finding("前缀跃动舞步♪锁定！后缀")]})["findings"][0]
    assert longer["canonical_resolution"] is None

    outside = refresh_canonical_resolutions(tmp_path, {"schema_version": 1, "findings": [_finding(prefix="114")]})["findings"][0]
    assert outside["canonical_resolution"] is None

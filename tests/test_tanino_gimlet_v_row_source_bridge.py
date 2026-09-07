from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import active_findings, refresh_canonical_resolutions
from scripts.harden_tanino_gimlet_v_row_source_bridge import RULE, SOURCE, TARGET, harden


def _seed(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    (glossary / "source_bridge_terms.json").write_text(
        json.dumps({"schema_version": 1, "policy": {}, "terms": [], "untrusted_sources": []}),
        encoding="utf-8",
    )
    (glossary / "terminology_reviews.json").write_text(
        json.dumps({"schema_version": 1, "decisions": []}), encoding="utf-8"
    )
    (glossary / "term_registry.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "ui_community_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "skill_name_style.json").write_text(json.dumps({"canonical_examples": []}), encoding="utf-8")


def _finding(prefix: list[str]) -> dict:
    return {
        "finding_id": "cf-46c6157b0331a647",
        "status": "open",
        "source_zh_cn": SOURCE,
        "match_mode": "exact",
        "source_paths": ["text_data_dict.json"],
        "key_exact": [],
        "json_path_prefixes": [prefix],
        "suggested_targets_vi": [],
        "canonical_resolution": None,
        "review_resolution": None,
    }


def test_hardener_resolves_exact_tanino_gimlet_profile_and_is_idempotent(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    bridge = json.loads((tmp_path / "glossary" / "source_bridge_terms.json").read_text(encoding="utf-8"))
    rule = next(item for item in bridge["terms"] if item["id"] == RULE["id"])
    assert rule["preferred"] == TARGET
    assert rule["source_paths"] == ["text_data_dict.json"]
    assert rule["json_path_prefixes"] == [["164", "1084"]]
    assert rule["match_mode"] == "exact"

    payload = refresh_canonical_resolutions(
        tmp_path, {"schema_version": 1, "findings": [_finding(["164", "1084"])]}
    )
    finding = payload["findings"][0]
    assert finding["canonical_resolution"] == {
        "layer": "source_bridge",
        "term_id": RULE["id"],
        "target_vi": TARGET,
    }
    assert active_findings(payload) == []


def test_rule_does_not_resolve_same_phrase_outside_exact_profile_item(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    payload = refresh_canonical_resolutions(
        tmp_path, {"schema_version": 1, "findings": [_finding(["164", "1085"])]}
    )
    assert payload["findings"][0]["canonical_resolution"] is None

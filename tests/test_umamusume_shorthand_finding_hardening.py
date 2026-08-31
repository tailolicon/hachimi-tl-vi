from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import refresh_canonical_resolutions
from scripts.harden_umamusume_shorthand_finding import UMAMUSUME_SHORTHAND_TEXT130, harden


def _seed(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    (glossary / "ui_community_terms.json").write_text(json.dumps({"schema_version": 1, "terms": []}), encoding="utf-8")
    (glossary / "terminology_reviews.json").write_text(json.dumps({"schema_version": 1, "decisions": []}), encoding="utf-8")
    (glossary / "term_registry.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "source_bridge_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")


def _finding(prefix: str) -> dict:
    return {
        "finding_id": "cf-test-umamusume-shorthand",
        "status": "open",
        "source_zh_cn": "马娘",
        "match_mode": "contains",
        "source_paths": ["text_data_dict.json"],
        "key_exact": [],
        "json_path_prefixes": [[prefix]],
        "suggested_targets_vi": ["Mã Nương"],
        "canonical_resolution": None,
        "review_resolution": None,
    }


def test_hardener_resolves_text130_shorthand_and_is_idempotent(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    community = json.loads((tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8"))
    rule = next(item for item in community["terms"] if item["id"] == UMAMUSUME_SHORTHAND_TEXT130["id"])
    assert rule["preferred"] == "Mã Nương"
    assert rule["json_path_prefixes"] == [["130"]]
    assert rule["match_mode"] == "contains"

    finding = refresh_canonical_resolutions(
        tmp_path,
        {"schema_version": 1, "findings": [_finding("130")]},
    )["findings"][0]
    assert finding["canonical_resolution"] == {
        "layer": "community",
        "term_id": "world.umamusume.shorthand.text130",
        "target_vi": "Mã Nương",
    }


def test_rule_does_not_resolve_same_shorthand_outside_text130(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    finding = refresh_canonical_resolutions(
        tmp_path,
        {"schema_version": 1, "findings": [_finding("128")]},
    )["findings"][0]
    assert finding["canonical_resolution"] is None

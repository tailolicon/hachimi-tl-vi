from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import refresh_canonical_resolutions
from scripts.harden_umamusume_shorthand_schedulebook_finding import (
    PREFERRED,
    SCHEDULEBOOK_KEYS,
    TERM_ID,
    UMAMUSUME_SHORTHAND_SCHEDULEBOOK,
    harden,
)


def _seed(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    (glossary / "ui_community_terms.json").write_text(json.dumps({"schema_version": 1, "terms": []}), encoding="utf-8")
    (glossary / "terminology_reviews.json").write_text(json.dumps({"schema_version": 1, "decisions": []}), encoding="utf-8")
    (glossary / "term_registry.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "source_bridge_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")


def _finding(key: str) -> dict:
    return {
        "finding_id": f"cf-test-umamusume-shorthand-{key}",
        "status": "open",
        "source_zh_cn": "马娘",
        "match_mode": "contains",
        "source_paths": ["localize_dict.json"],
        "key_exact": [key],
        "json_path_prefixes": [],
        "suggested_targets_vi": [PREFERRED],
        "canonical_resolution": None,
        "review_resolution": None,
    }


def test_hardener_resolves_all_reviewed_schedulebook_shorthand_findings(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    community = json.loads((tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8"))
    rule = next(item for item in community["terms"] if item["id"] == TERM_ID)
    assert rule == UMAMUSUME_SHORTHAND_SCHEDULEBOOK

    findings = [_finding(key) for key in SCHEDULEBOOK_KEYS]
    refreshed = refresh_canonical_resolutions(
        tmp_path,
        {"schema_version": 1, "findings": findings},
    )["findings"]
    assert [row["canonical_resolution"] for row in refreshed] == [
        {"layer": "community", "term_id": TERM_ID, "target_vi": PREFERRED}
        for _ in SCHEDULEBOOK_KEYS
    ]


def test_rule_does_not_resolve_unreviewed_localize_key(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    finding = refresh_canonical_resolutions(
        tmp_path,
        {"schema_version": 1, "findings": [_finding("ScheduleBook499999")]},
    )["findings"][0]
    assert finding["canonical_resolution"] is None

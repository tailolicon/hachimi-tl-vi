from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import active_findings, refresh_canonical_resolutions
from scripts.harden_reisou_ichoku_ramen_do_finding import (
    DECISION,
    HISTORICAL,
    PATH_PREFIX,
    PREFERRED,
    SOURCE_JA,
    SOURCE_ZH,
    TERM,
    harden,
)

FINDING_ID = "cf-2f9d7a7320e1c5db"


def _seed(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    for name, payload in [
        ("ui_community_terms.json", {"schema_version": 1, "terms": []}),
        ("terminology_reviews.json", {"schema_version": 1, "decisions": []}),
        ("term_registry.json", {"terms": []}),
        ("source_bridge_terms.json", {"terms": []}),
        ("skill_name_style.json", {"canonical_examples": []}),
    ]:
        (glossary / name).write_text(json.dumps(payload), encoding="utf-8")


def _finding(*, source: str = SOURCE_ZH, prefix: list[str] | None = None, source_path: str = "text_data_dict.json") -> dict:
    return {
        "finding_id": FINDING_ID,
        "status": "open",
        "source_zh_cn": source,
        "match_mode": "exact",
        "source_paths": [source_path],
        "key_exact": [],
        "json_path_prefixes": [PATH_PREFIX if prefix is None else prefix],
        "suggested_targets_vi": [],
        "canonical_resolution": None,
        "review_resolution": {"decision_id": "old.defer", "action": "defer", "target_vi": None},
    }


def test_hardener_locks_verified_skill_and_is_idempotent(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    community = json.loads((tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8"))
    rule = next(item for item in community["terms"] if item["id"] == TERM["id"])
    assert rule["preferred"] == PREFERRED
    assert rule["accepted"] == [PREFERRED]
    assert HISTORICAL in rule["forbidden"]
    assert rule["json_path_prefixes"] == [PATH_PREFIX]
    assert rule["match_mode"] == "exact"

    reviews = json.loads((tmp_path / "glossary" / "terminology_reviews.json").read_text(encoding="utf-8"))
    decision = next(item for item in reviews["decisions"] if item["decision_id"] == DECISION["decision_id"])
    assert decision["ja"] == [SOURCE_JA]
    assert decision["target_vi"] == PREFERRED

    resolved = refresh_canonical_resolutions(tmp_path, {"schema_version": 1, "findings": [_finding()]})
    finding = resolved["findings"][0]
    assert finding["canonical_resolution"] == {
        "layer": "community",
        "term_id": TERM["id"],
        "target_vi": PREFERRED,
    }
    assert finding["review_resolution"] == {
        "decision_id": DECISION["decision_id"],
        "action": "lock",
        "target_vi": PREFERRED,
    }
    assert active_findings(resolved) == []


def test_exact_category_scope_does_not_overmatch(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    for finding in [
        _finding(source=SOURCE_ZH + "追加"),
        _finding(prefix=["172"]),
        _finding(source_path="localize_dict.json"),
    ]:
        finding["review_resolution"] = None
        resolved = refresh_canonical_resolutions(tmp_path, {"schema_version": 1, "findings": [finding]})["findings"][0]
        assert resolved["canonical_resolution"] is None

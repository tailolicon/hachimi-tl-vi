from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import refresh_canonical_resolutions
from scripts.harden_transcend_overdrive_finding import DECISION, PREFERRED, SOURCE_JA, SOURCE_ZH, TERM_ID, harden

FINDING_ID = "cf-836c3861f2d917ca"


def _seed(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    (glossary / "ui_community_terms.json").write_text(json.dumps({"schema_version": 1, "terms": []}), encoding="utf-8")
    (glossary / "terminology_reviews.json").write_text(json.dumps({"schema_version": 1, "decisions": []}), encoding="utf-8")
    (glossary / "term_registry.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "source_bridge_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "skill_name_style.json").write_text(json.dumps({"canonical_examples": []}), encoding="utf-8")


def _finding(*, prefix: list[list[str]] | None = None, source_path: str = "text_data_dict.json") -> dict[str, object]:
    return {
        "finding_id": FINDING_ID,
        "status": "open",
        "source_zh_cn": SOURCE_ZH,
        "match_mode": "exact",
        "source_paths": [source_path],
        "key_exact": [],
        "json_path_prefixes": prefix if prefix is not None else [["147"]],
        "suggested_targets_vi": [],
        "canonical_resolution": None,
        "review_resolution": None,
    }


def test_transcend_overdrive_resolves_live_skill_finding(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    community = json.loads((tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8"))
    rule = next(item for item in community["terms"] if item["id"] == TERM_ID)
    assert rule["preferred"] == PREFERRED
    assert rule["accepted"] == [PREFERRED]
    assert rule["source_paths"] == ["text_data_dict.json"]
    assert rule["json_path_prefixes"] == [["147"]]
    assert rule["match_mode"] == "exact"

    reviews = json.loads((tmp_path / "glossary" / "terminology_reviews.json").read_text(encoding="utf-8"))
    decision = next(item for item in reviews["decisions"] if item["decision_id"] == DECISION["decision_id"])
    assert decision["ja"] == [SOURCE_JA]
    assert decision["target_vi"] == PREFERRED

    finding = refresh_canonical_resolutions(tmp_path, {"schema_version": 1, "findings": [_finding()]})["findings"][0]
    assert finding["review_resolution"] == {
        "decision_id": "audit.finding.skill-transcend-overdrive",
        "action": "lock",
        "target_vi": PREFERRED,
    }
    assert finding["canonical_resolution"] == {
        "layer": "community",
        "term_id": TERM_ID,
        "target_vi": PREFERRED,
    }


def test_transcend_overdrive_rule_is_category_and_path_scoped(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True

    wrong_category = refresh_canonical_resolutions(
        tmp_path,
        {"schema_version": 1, "findings": [_finding(prefix=[["144"]])]},
    )["findings"][0]
    assert wrong_category["canonical_resolution"] is None

    wrong_path = refresh_canonical_resolutions(
        tmp_path,
        {"schema_version": 1, "findings": [_finding(source_path="localize_dict.json")]},
    )["findings"][0]
    assert wrong_path["canonical_resolution"] is None

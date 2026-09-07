from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import active_findings, refresh_canonical_resolutions
from scripts.harden_bucchigiri_road_finding import (
    DECISION,
    FINDING_ID,
    INHERITANCE_FINDING_ID,
    INHERITANCE_RULE,
    RULE,
    harden,
)


def _title_finding(prefix: str = "147") -> dict[str, object]:
    return {
        "finding_id": FINDING_ID,
        "status": "open",
        "source_zh_cn": "冠绝之路",
        "match_mode": "exact",
        "source_paths": ["text_data_dict.json"],
        "key_exact": [],
        "json_path_prefixes": [[prefix]],
        "suggested_targets_vi": [],
        "canonical_resolution": None,
        "review_resolution": None,
    }


def _inheritance_finding(
    prefixes: list[list[str]] | None = None,
    *,
    source_path: str = "text_data_dict.json",
) -> dict[str, object]:
    return {
        "finding_id": INHERITANCE_FINDING_ID,
        "status": "open",
        "source_zh_cn": "冠绝之路",
        "match_mode": "contains",
        "source_paths": [source_path],
        "key_exact": [],
        "json_path_prefixes": [] if prefixes is None else prefixes,
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
    (glossary / "term_registry.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "source_bridge_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "canonical_findings.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "findings": [_title_finding(), _inheritance_finding()],
            }
        ),
        encoding="utf-8",
    )


def test_keep_pushing_ahead_resolves_title_and_inheritance_context(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    community = json.loads(
        (tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8")
    )
    title_rule = next(item for item in community["terms"] if item["id"] == RULE["id"])
    inheritance_rule = next(
        item for item in community["terms"] if item["id"] == INHERITANCE_RULE["id"]
    )
    assert title_rule["json_path_prefixes"] == [["147"]]
    assert title_rule["match_mode"] == "exact"
    assert inheritance_rule["json_path_prefixes"] == [["172"]]
    assert inheritance_rule["match_mode"] == "contains"
    assert inheritance_rule["preferred"] == "Keep Pushing Ahead"

    reviews = json.loads(
        (tmp_path / "glossary" / "terminology_reviews.json").read_text(encoding="utf-8")
    )
    decision = next(
        item for item in reviews["decisions"] if item["decision_id"] == DECISION["decision_id"]
    )
    assert decision["target_vi"] == "Keep Pushing Ahead"
    assert decision["ja"] == ["ぶっちぎりロード"]

    ledger = json.loads(
        (tmp_path / "glossary" / "canonical_findings.json").read_text(encoding="utf-8")
    )
    inheritance = next(
        item for item in ledger["findings"] if item["finding_id"] == INHERITANCE_FINDING_ID
    )
    assert inheritance["json_path_prefixes"] == [["172"]]
    assert inheritance["suggested_targets_vi"] == ["Keep Pushing Ahead"]

    refreshed = refresh_canonical_resolutions(tmp_path, ledger)
    title = next(item for item in refreshed["findings"] if item["finding_id"] == FINDING_ID)
    inheritance = next(
        item for item in refreshed["findings"] if item["finding_id"] == INHERITANCE_FINDING_ID
    )
    assert title["canonical_resolution"] == {
        "layer": "community",
        "term_id": "skill.mejiro_palmer.keep_pushing_ahead",
        "target_vi": "Keep Pushing Ahead",
    }
    assert inheritance["canonical_resolution"] == {
        "layer": "community",
        "term_id": "skill.mejiro_palmer.keep_pushing_ahead.inheritance172",
        "target_vi": "Keep Pushing Ahead",
    }
    assert INHERITANCE_FINDING_ID not in {x["finding_id"] for x in active_findings(refreshed)}


def test_inheritance_rule_does_not_resolve_unrelated_category(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True

    ledger = {"schema_version": 1, "findings": [_inheritance_finding([["16"]])]}
    finding = refresh_canonical_resolutions(tmp_path, ledger)["findings"][0]
    assert finding["review_resolution"]["target_vi"] == "Keep Pushing Ahead"
    assert finding["canonical_resolution"] is None


def test_inheritance_rule_does_not_resolve_other_source_file(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True

    ledger = {
        "schema_version": 1,
        "findings": [_inheritance_finding([["172"]], source_path="localize_dict.json")],
    }
    finding = refresh_canonical_resolutions(tmp_path, ledger)["findings"][0]
    assert finding["review_resolution"]["target_vi"] == "Keep Pushing Ahead"
    assert finding["canonical_resolution"] is None

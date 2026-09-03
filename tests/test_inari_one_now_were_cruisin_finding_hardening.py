from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import active_findings, refresh_canonical_resolutions
from scripts.harden_inari_one_now_were_cruisin_finding import (
    DECISION,
    FACTOR_TERM_ID,
    FINDING_ID,
    PREFERRED,
    SOURCE_JA,
    SOURCE_ZH_FACTOR,
    SOURCE_ZH_TITLE,
    TITLE_TERM_ID,
    harden,
)


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


def _finding(
    source: str = SOURCE_ZH_FACTOR,
    *,
    prefix: str = "172",
    source_path: str = "text_data_dict.json",
    match_mode: str = "contains",
) -> dict[str, object]:
    return {
        "finding_id": FINDING_ID,
        "status": "open",
        "source_zh_cn": source,
        "match_mode": match_mode,
        "source_paths": [source_path],
        "key_exact": [],
        "json_path_prefixes": [[prefix]],
        "suggested_targets_vi": [],
        "canonical_resolution": None,
        "review_resolution": None,
    }


def test_inari_one_factor_finding_resolves_and_hardener_is_idempotent(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    community = json.loads((tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8"))
    factor = next(item for item in community["terms"] if item["id"] == FACTOR_TERM_ID)
    title = next(item for item in community["terms"] if item["id"] == TITLE_TERM_ID)
    assert factor["preferred"] == PREFERRED
    assert factor["json_path_prefixes"] == [["172"]]
    assert factor["match_mode"] == "contains"
    assert factor["invalidation_scope"] == "item"
    assert title["preferred"] == PREFERRED
    assert title["json_path_prefixes"] == [["147"]]
    assert title["match_mode"] == "exact"

    reviews = json.loads((tmp_path / "glossary" / "terminology_reviews.json").read_text(encoding="utf-8"))
    decision = next(item for item in reviews["decisions"] if item["decision_id"] == DECISION["decision_id"])
    assert decision["target_vi"] == PREFERRED
    assert decision["ja"] == [SOURCE_JA]
    assert decision["json_path_prefixes"] == [["172"]]

    payload = refresh_canonical_resolutions(
        tmp_path, {"schema_version": 1, "findings": [_finding()]}
    )
    finding = payload["findings"][0]
    assert finding["canonical_resolution"] == {
        "layer": "community",
        "term_id": FACTOR_TERM_ID,
        "target_vi": PREFERRED,
    }
    assert finding["review_resolution"] == {
        "decision_id": DECISION["decision_id"],
        "action": "lock",
        "target_vi": PREFERRED,
    }
    assert active_findings(payload) == []


def test_title_rule_resolves_only_proven_category_and_path(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True

    title = refresh_canonical_resolutions(
        tmp_path,
        {"schema_version": 1, "findings": [_finding(SOURCE_ZH_TITLE, prefix="147", match_mode="exact")]},
    )["findings"][0]
    assert title["canonical_resolution"] == {
        "layer": "community",
        "term_id": TITLE_TERM_ID,
        "target_vi": PREFERRED,
    }

    wrong_category = refresh_canonical_resolutions(
        tmp_path, {"schema_version": 1, "findings": [_finding(prefix="167")]}
    )["findings"][0]
    assert wrong_category["canonical_resolution"] is None

    wrong_path = refresh_canonical_resolutions(
        tmp_path,
        {"schema_version": 1, "findings": [_finding(source_path="localize_dict.json")]},
    )["findings"][0]
    assert wrong_path["canonical_resolution"] is None

from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import active_findings, refresh_canonical_resolutions
from scripts.harden_prix_arc_category130_finding import (
    DECISION,
    FINDING_ID,
    RULE,
    SOURCE_JA,
    SOURCE_ZH,
    TARGET,
    harden,
)
from scripts.translation_review_common import community_term_matches, load_community_terms


def _finding(*, source_path: str = "text_data_dict.json") -> dict:
    return {
        "finding_id": FINDING_ID,
        "status": "open",
        "source_zh_cn": SOURCE_ZH,
        "match_mode": "contains",
        "source_paths": [source_path],
        "key_exact": [],
        "json_path_prefixes": [],
        "suggested_targets_vi": [TARGET],
        "canonical_resolution": None,
        "review_resolution": None,
    }


def _seed(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    (glossary / "ui_community_terms.json").write_text(json.dumps({"schema_version": 1, "terms": []}), encoding="utf-8")
    (glossary / "terminology_reviews.json").write_text(json.dumps({"schema_version": 1, "decisions": []}), encoding="utf-8")
    (glossary / "canonical_findings.json").write_text(json.dumps({"schema_version": 1, "findings": [_finding()]}), encoding="utf-8")
    (glossary / "term_registry.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "source_bridge_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "skill_name_style.json").write_text(json.dumps({"canonical_examples": []}), encoding="utf-8")


def test_hardener_resolves_prix_arc_reference_and_is_idempotent(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    community = json.loads((tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8"))
    rule = next(item for item in community["terms"] if item["id"] == RULE["id"])
    assert rule["preferred"] == TARGET
    assert rule["source_paths"] == ["text_data_dict.json"]
    assert rule["match_mode"] == "contains"
    assert rule["invalidation_scope"] == "item"

    reviews = json.loads((tmp_path / "glossary" / "terminology_reviews.json").read_text(encoding="utf-8"))
    decision = next(item for item in reviews["decisions"] if item["decision_id"] == DECISION["decision_id"])
    assert decision["target_vi"] == TARGET
    assert decision["ja"] == [SOURCE_JA]

    ledger = json.loads((tmp_path / "glossary" / "canonical_findings.json").read_text(encoding="utf-8"))
    resolved_ledger = refresh_canonical_resolutions(tmp_path, ledger)
    resolved = resolved_ledger["findings"][0]
    assert resolved["canonical_resolution"] == {
        "layer": "community",
        "term_id": RULE["id"],
        "target_vi": TARGET,
    }
    assert resolved["review_resolution"] == {
        "decision_id": DECISION["decision_id"],
        "action": "lock",
        "target_vi": TARGET,
    }
    assert active_findings(resolved_ledger) == []


def test_rule_covers_category130_reference_but_not_localize_dict(tmp_path: Path) -> None:
    _seed(tmp_path)
    harden(tmp_path)
    terms = load_community_terms(tmp_path)

    category130 = community_term_matches(
        None,
        f"{SOURCE_ZH}赛马娘",
        f"{TARGET} Mã Nương",
        terms,
        source_path="text_data_dict.json",
        json_path=["130", "291"],
    )
    assert RULE["id"] in {item["id"] for item in category130}

    wrong_path = community_term_matches(
        None,
        SOURCE_ZH,
        TARGET,
        terms,
        source_path="localize_dict.json",
        json_path=["Race9999"],
    )
    assert RULE["id"] not in {item["id"] for item in wrong_path}

    wrong_finding = _finding(source_path="localize_dict.json")
    assert refresh_canonical_resolutions(tmp_path, {"schema_version": 1, "findings": [wrong_finding]})["findings"][0]["canonical_resolution"] is None

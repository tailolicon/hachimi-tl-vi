from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import active_findings, refresh_canonical_resolutions
from scripts.harden_cesario_guiding_sea_finding import (
    DECISION_ID,
    FINDING_ID,
    PATH_PREFIXES,
    RULE_ID,
    SOURCE_ZH,
    TARGET,
    harden,
)


def _finding(prefixes: list[list[str]] | None = None) -> dict:
    return {
        "finding_id": FINDING_ID,
        "status": "open",
        "source_zh_cn": SOURCE_ZH,
        "match_mode": "contains",
        "source_paths": ["text_data_dict.json"],
        "key_exact": [],
        "json_path_prefixes": [] if prefixes is None else prefixes,
        "suggested_targets_vi": [],
        "canonical_resolution": None,
        "review_resolution": None,
    }


def _seed(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir(parents=True)
    (glossary / "ui_community_terms.json").write_text(
        json.dumps({"schema_version": 1, "terms": []}), encoding="utf-8"
    )
    (glossary / "terminology_reviews.json").write_text(
        json.dumps({"schema_version": 1, "decisions": []}), encoding="utf-8"
    )
    (glossary / "canonical_findings.json").write_text(
        json.dumps({"schema_version": 1, "findings": [_finding()]}), encoding="utf-8"
    )
    (glossary / "term_registry.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "source_bridge_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "skill_name_style.json").write_text(json.dumps({"canonical_examples": []}), encoding="utf-8")


def test_hardener_scopes_and_resolves_guiding_sea(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    community = json.loads((tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8"))
    rule = next(item for item in community["terms"] if item["id"] == RULE_ID)
    assert rule["preferred"] == TARGET
    assert rule["accepted"] == [TARGET]
    assert rule["match_mode"] == "contains"
    assert rule["json_path_prefixes"] == PATH_PREFIXES

    reviews = json.loads((tmp_path / "glossary" / "terminology_reviews.json").read_text(encoding="utf-8"))
    decision = next(item for item in reviews["decisions"] if item["decision_id"] == DECISION_ID)
    assert decision["target_vi"] == TARGET
    assert decision["json_path_prefixes"] == PATH_PREFIXES

    ledger = json.loads((tmp_path / "glossary" / "canonical_findings.json").read_text(encoding="utf-8"))
    finding = ledger["findings"][0]
    assert finding["json_path_prefixes"] == PATH_PREFIXES
    assert finding["suggested_targets_vi"] == [TARGET]

    resolved = refresh_canonical_resolutions(tmp_path, ledger)
    finding = resolved["findings"][0]
    assert finding["canonical_resolution"] == {
        "layer": "community",
        "term_id": RULE_ID,
        "target_vi": TARGET,
    }
    assert finding["review_resolution"] == {
        "decision_id": DECISION_ID,
        "action": "lock",
        "target_vi": TARGET,
    }
    assert active_findings(resolved) == []


def test_scope_prevents_generic_idiom_outside_inheritance_category(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True

    # The canonical rule must not claim an otherwise-identical finding outside category 172.
    outside = _finding(prefixes=[["163"]])
    outside["suggested_targets_vi"] = [TARGET]
    outside_resolved = refresh_canonical_resolutions(
        tmp_path, {"schema_version": 1, "findings": [outside]}
    )["findings"][0]
    assert outside_resolved["canonical_resolution"] is None
    assert outside_resolved["review_resolution"] is None

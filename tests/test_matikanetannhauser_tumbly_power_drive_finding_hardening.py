from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import active_findings, refresh_canonical_resolutions
from scripts.harden_matikanetannhauser_tumbly_power_drive_finding import (
    DECISION,
    FINDING_ID,
    PREFERRED,
    SOURCE_JA,
    SOURCE_ZH,
    TERM,
    TERM_ID,
    harden,
)


def _finding(*, source_path: str = "text_data_dict.json") -> dict:
    return {
        "finding_id": FINDING_ID,
        "status": "open",
        "source_zh_cn": SOURCE_ZH,
        "match_mode": "contains",
        "source_paths": [source_path],
        "key_exact": [],
        "json_path_prefixes": [],
        "suggested_targets_vi": [],
        "canonical_resolution": None,
        "review_resolution": {
            "decision_id": "parallel.ctx-67f8551f77807292-v1.term-0083.12",
            "action": "defer",
            "target_vi": None,
        },
    }


def _seed(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    (glossary / "ui_community_terms.json").write_text(
        json.dumps({"schema_version": 1, "terms": []}), encoding="utf-8"
    )
    (glossary / "terminology_reviews.json").write_text(
        json.dumps({"schema_version": 1, "decisions": [{
            "decision_id": "parallel.ctx-67f8551f77807292-v1.term-0083.12",
            "source_zh_cn": SOURCE_ZH,
            "action": "defer",
            "target_vi": None,
        }]}), encoding="utf-8"
    )
    (glossary / "canonical_findings.json").write_text(
        json.dumps({"schema_version": 1, "findings": [_finding()]}), encoding="utf-8"
    )
    (glossary / "term_registry.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "source_bridge_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "skill_name_style.json").write_text(
        json.dumps({"canonical_examples": []}), encoding="utf-8"
    )


def test_hardener_resolves_live_finding_and_is_idempotent(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    community = json.loads((tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8"))
    rule = next(item for item in community["terms"] if item["id"] == TERM_ID)
    assert rule == TERM
    assert rule["preferred"] == PREFERRED == "Lăn Tròn!? Power Drive"
    assert rule["source_aliases"] == [SOURCE_ZH]
    assert rule["match_mode"] == "contains"
    assert rule["source_paths"] == ["text_data_dict.json"]

    reviews = json.loads((tmp_path / "glossary" / "terminology_reviews.json").read_text(encoding="utf-8"))
    decision = next(item for item in reviews["decisions"] if item["decision_id"] == DECISION["decision_id"])
    assert decision["action"] == "lock"
    assert decision["target_vi"] == PREFERRED
    assert decision["ja"] == [SOURCE_JA]

    ledger = json.loads((tmp_path / "glossary" / "canonical_findings.json").read_text(encoding="utf-8"))
    resolved = refresh_canonical_resolutions(tmp_path, ledger)
    row = resolved["findings"][0]
    assert row["canonical_resolution"] == {
        "layer": "community",
        "term_id": TERM_ID,
        "target_vi": PREFERRED,
    }
    assert row["review_resolution"] == {
        "decision_id": DECISION["decision_id"],
        "action": "lock",
        "target_vi": PREFERRED,
    }
    assert active_findings(resolved) == []


def test_rule_does_not_cover_other_source_file(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    outside = _finding(source_path="localize_dict.json")
    resolved = refresh_canonical_resolutions(
        tmp_path, {"schema_version": 1, "findings": [outside]}
    )["findings"][0]
    assert resolved["canonical_resolution"] is None

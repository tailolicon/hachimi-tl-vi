import json
from pathlib import Path

from scripts.canonical_findings import refresh_canonical_resolutions
from scripts.harden_grand_live_mental_finding import (
    GRAND_LIVE_MENTAL_DECISION,
    GRAND_LIVE_MENTAL_TEXT,
    GRAND_LIVE_MENTAL_UI,
    OBSOLETE_TEXT_RULE_ID,
    harden,
)


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _finding(source_path: str = "text_data_dict.json") -> dict:
    return {
        "finding_id": "cf-test-grand-live-mental",
        "status": "open",
        "source_zh_cn": "心理值",
        "match_mode": "contains",
        "source_paths": [source_path],
        "key_exact": [],
        "json_path_prefixes": [],
        "kinds": ["system_label"],
        "concepts": ["Grand Live performance stat: Mental"],
        "suggested_targets_vi": ["Mental"],
        "confidence_levels": ["high"],
        "reasons": ["Grand Live system label"],
        "evidence_count": 1,
        "evidence": [
            {
                "uid": "zhcn:test",
                "source_path": source_path,
                "json_path": ["131", "241"],
                "source_text": "获得合计300点以上心理值完成育成",
                "current_text": "Đạt ít nhất 300 điểm Tinh thần",
            }
        ],
        "canonical_resolution": None,
        "review_resolution": None,
    }


def test_hardener_matches_live_text_data_finding_scope_and_is_idempotent(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    _write(
        glossary / "ui_community_terms.json",
        {
            "schema_version": 1,
            "terms": [
                {
                    "id": OBSOLETE_TEXT_RULE_ID,
                    "source_aliases": ["心理值"],
                    "preferred": "Mental",
                    "source_paths": ["text_data_dict.json"],
                    "json_path_prefixes": [["131"]],
                }
            ],
        },
    )
    _write(glossary / "terminology_reviews.json", {"schema_version": 1, "decisions": []})
    _write(glossary / "term_registry.json", {"schema_version": 1, "terms": []})
    _write(glossary / "source_bridge_terms.json", {"schema_version": 1, "terms": []})

    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    community = json.loads((glossary / "ui_community_terms.json").read_text(encoding="utf-8"))
    by_id = {item["id"]: item for item in community["terms"]}
    assert OBSOLETE_TEXT_RULE_ID not in by_id
    assert by_id[GRAND_LIVE_MENTAL_TEXT["id"]]["preferred"] == "Mental"
    assert by_id[GRAND_LIVE_MENTAL_TEXT["id"]]["source_paths"] == ["text_data_dict.json"]
    assert by_id[GRAND_LIVE_MENTAL_TEXT["id"]]["json_path_prefixes"] == []
    assert by_id[GRAND_LIVE_MENTAL_UI["id"]]["key_exact"] == ["SingleModeScenarioLive0005"]

    reviews = json.loads((glossary / "terminology_reviews.json").read_text(encoding="utf-8"))
    by_decision = {item["decision_id"]: item for item in reviews["decisions"]}
    assert by_decision[GRAND_LIVE_MENTAL_DECISION["decision_id"]]["target_vi"] == "Mental"

    ledger = refresh_canonical_resolutions(
        tmp_path,
        {"schema_version": 1, "policy": {"canonical": False}, "findings": [_finding()]},
    )
    assert ledger["findings"][0]["canonical_resolution"] == {
        "layer": "community",
        "term_id": GRAND_LIVE_MENTAL_TEXT["id"],
        "target_vi": "Mental",
    }


def test_text_data_rule_does_not_resolve_other_source_paths(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    _write(glossary / "ui_community_terms.json", {"schema_version": 1, "terms": []})
    _write(glossary / "terminology_reviews.json", {"schema_version": 1, "decisions": []})
    _write(glossary / "term_registry.json", {"schema_version": 1, "terms": []})
    _write(glossary / "source_bridge_terms.json", {"schema_version": 1, "terms": []})

    assert harden(tmp_path) is True
    ledger = refresh_canonical_resolutions(
        tmp_path,
        {"schema_version": 1, "policy": {"canonical": False}, "findings": [_finding("storytimeline.json")]},
    )
    assert ledger["findings"][0]["canonical_resolution"] is None

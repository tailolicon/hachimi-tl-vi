import json
from pathlib import Path

from scripts.canonical_findings import refresh_canonical_resolutions
from scripts.harden_loh_main_stage_alias_finding import (
    ALIAS,
    BASE_TERM_ID,
    BRIDGE_TERM_ID,
    DECISION_ID,
    harden,
)


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _finding(source_path: str = "localize_dict.json") -> dict:
    return {
        "finding_id": "cf-test-loh-main-stage-alias",
        "status": "open",
        "source_zh_cn": ALIAS,
        "match_mode": "contains",
        "source_paths": [source_path],
        "key_exact": [],
        "json_path_prefixes": [],
        "kinds": ["terminology"],
        "concepts": ["League of Heroes Main Stage alias"],
        "suggested_targets_vi": [],
        "confidence_levels": ["high"],
        "reasons": ["Event-specific Main Stage alias."],
        "evidence_count": 1,
        "evidence": [],
        "canonical_resolution": None,
        "review_resolution": None,
    }


def _community() -> dict:
    return {
        "schema_version": 1,
        "terms": [
            {
                "id": BASE_TERM_ID,
                "category": "stage",
                "key_prefixes": ["Heroes"],
                "source_aliases": ["メインステージ", "主要阶段"],
                "preferred": "Main Stage",
                "compact": [],
                "accepted": ["Main Stage"],
                "forbidden": ["Giai đoạn chính"],
                "require_accepted": True,
                "basis": "League of Heroes named stage.",
            }
        ],
    }


def _seed(tmp_path: Path) -> Path:
    glossary = tmp_path / "glossary"
    _write(glossary / "ui_community_terms.json", _community())
    _write(glossary / "terminology_reviews.json", {"schema_version": 1, "decisions": []})
    _write(glossary / "term_registry.json", {"schema_version": 1, "terms": []})
    _write(glossary / "source_bridge_terms.json", {"schema_version": 1, "terms": []})
    return glossary


def test_hardener_review_locks_bridge_and_resolves_live_scope(tmp_path: Path) -> None:
    glossary = _seed(tmp_path)

    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    community = json.loads((glossary / "ui_community_terms.json").read_text(encoding="utf-8"))
    base = next(item for item in community["terms"] if item["id"] == BASE_TERM_ID)
    bridge = next(item for item in community["terms"] if item["id"] == BRIDGE_TERM_ID)
    assert base["key_prefixes"] == ["Heroes"]
    assert ALIAS not in base["source_aliases"]
    assert bridge["source_aliases"] == [ALIAS]
    assert bridge["source_paths"] == ["localize_dict.json"]

    reviews = json.loads((glossary / "terminology_reviews.json").read_text(encoding="utf-8"))
    decision = next(item for item in reviews["decisions"] if item["decision_id"] == DECISION_ID)
    assert decision["action"] == "lock"
    assert decision["target_vi"] == "Main Stage"

    ledger = refresh_canonical_resolutions(
        tmp_path,
        {"schema_version": 1, "policy": {"canonical": False}, "findings": [_finding()]},
    )
    finding = ledger["findings"][0]
    assert finding["review_resolution"] == {
        "decision_id": DECISION_ID,
        "action": "lock",
        "target_vi": "Main Stage",
    }
    assert finding["canonical_resolution"] == {
        "layer": "community",
        "term_id": BRIDGE_TERM_ID,
        "target_vi": "Main Stage",
    }


def test_reviewed_bridge_does_not_canonicalize_outside_localize_source(tmp_path: Path) -> None:
    _seed(tmp_path)

    assert harden(tmp_path) is True
    ledger = refresh_canonical_resolutions(
        tmp_path,
        {"schema_version": 1, "policy": {"canonical": False}, "findings": [_finding("storytimeline.json")]},
    )
    finding = ledger["findings"][0]
    assert finding["review_resolution"]["action"] == "lock"
    assert finding["canonical_resolution"] is None

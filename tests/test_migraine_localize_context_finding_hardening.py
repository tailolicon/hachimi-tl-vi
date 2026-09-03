import json
from pathlib import Path

from scripts.canonical_findings import refresh_canonical_resolutions
from scripts.harden_migraine_localize_context_finding import (
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
        "finding_id": "cf-e311d621cf5334b2",
        "status": "open",
        "source_zh_cn": ALIAS,
        "match_mode": "contains",
        "source_paths": [source_path],
        "key_exact": [],
        "json_path_prefixes": [],
        "kinds": ["terminology"],
        "concepts": ["Named gameplay Condition: Migraine"],
        "suggested_targets_vi": ["Migraine"],
        "confidence_levels": ["high"],
        "reasons": ["Named Conditions use established English player-facing names."],
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
                "category": "condition",
                "source_aliases": [ALIAS],
                "preferred": "Migraine",
                "compact": [],
                "accepted": ["Migraine"],
                "forbidden": ["Đau nửa đầu"],
                "require_accepted": True,
                "basis": "Named negative Condition; established Global name Migraine.",
                "invalidation_scope": "item",
                "source_paths": ["text_data_dict.json"],
                "json_path_prefixes": [["142"]],
                "match_mode": "exact",
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


def test_hardener_preserves_table_term_and_resolves_localize_condition_reference(tmp_path: Path) -> None:
    glossary = _seed(tmp_path)

    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    community = json.loads((glossary / "ui_community_terms.json").read_text(encoding="utf-8"))
    base = next(item for item in community["terms"] if item["id"] == BASE_TERM_ID)
    bridge = next(item for item in community["terms"] if item["id"] == BRIDGE_TERM_ID)
    assert base["source_paths"] == ["text_data_dict.json"]
    assert base["json_path_prefixes"] == [["142"]]
    assert bridge["source_paths"] == ["localize_dict.json"]
    assert bridge["match_mode"] == "contains"

    reviews = json.loads((glossary / "terminology_reviews.json").read_text(encoding="utf-8"))
    decision = next(item for item in reviews["decisions"] if item["decision_id"] == DECISION_ID)
    assert decision["action"] == "lock"
    assert decision["target_vi"] == "Migraine"

    finding = refresh_canonical_resolutions(
        tmp_path,
        {"schema_version": 1, "policy": {"canonical": False}, "findings": [_finding()]},
    )["findings"][0]
    assert finding["review_resolution"] == {
        "decision_id": DECISION_ID,
        "action": "lock",
        "target_vi": "Migraine",
    }
    assert finding["canonical_resolution"] == {
        "layer": "community",
        "term_id": BRIDGE_TERM_ID,
        "target_vi": "Migraine",
    }


def test_reviewed_migraine_does_not_canonicalize_unquoted_other_source(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    finding = refresh_canonical_resolutions(
        tmp_path,
        {"schema_version": 1, "policy": {"canonical": False}, "findings": [_finding("storytimeline.json")]},
    )["findings"][0]
    assert finding["review_resolution"]["action"] == "lock"
    assert finding["canonical_resolution"] is None

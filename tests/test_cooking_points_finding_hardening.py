import json
from pathlib import Path

from scripts.canonical_findings import refresh_canonical_resolutions
from scripts.harden_cooking_points_finding import ALIAS, DECISION_ID, FINDING_ID, TARGET, TERM_ID, harden


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _finding(source_path: str = "localize_dict.json") -> dict:
    return {
        "finding_id": FINDING_ID,
        "status": "open",
        "source_zh_cn": ALIAS,
        "match_mode": "contains",
        "source_paths": [source_path],
        "key_exact": [],
        "json_path_prefixes": [],
        "kinds": ["system_label"],
        "concepts": ["Cooking scenario points label"],
        "suggested_targets_vi": ["Pt Món ăn"],
        "confidence_levels": ["high"],
        "reasons": ["Reusable scenario label requires canonical identity."],
        "evidence_count": 1,
        "evidence": [],
        "canonical_resolution": None,
        "review_resolution": None,
    }


def _seed(tmp_path: Path) -> Path:
    glossary = tmp_path / "glossary"
    _write(glossary / "ui_community_terms.json", {"schema_version": 1, "terms": []})
    _write(glossary / "terminology_reviews.json", {"schema_version": 1, "decisions": []})
    _write(glossary / "term_registry.json", {"schema_version": 1, "terms": []})
    _write(glossary / "source_bridge_terms.json", {"schema_version": 1, "terms": []})
    _write(glossary / "canonical_findings.json", {"schema_version": 1, "findings": [_finding()]})
    return glossary


def test_hardener_is_idempotent_and_resolves_cooking_points(tmp_path: Path) -> None:
    glossary = _seed(tmp_path)

    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    community = json.loads((glossary / "ui_community_terms.json").read_text(encoding="utf-8"))
    term = next(item for item in community["terms"] if item["id"] == TERM_ID)
    assert term["preferred"] == TARGET
    assert term["source_aliases"] == [ALIAS]
    assert term["source_paths"] == ["localize_dict.json"]
    assert term["match_mode"] == "contains"
    assert "Pt Món ăn" in term["forbidden"]
    assert "Pt Nấu ăn" in term["forbidden"]

    ledger = refresh_canonical_resolutions(
        tmp_path,
        {"schema_version": 1, "policy": {"canonical": False}, "findings": [_finding()]},
    )
    finding = ledger["findings"][0]
    assert finding["review_resolution"] == {
        "decision_id": DECISION_ID,
        "action": "lock",
        "target_vi": TARGET,
    }
    assert finding["canonical_resolution"] == {
        "layer": "community",
        "term_id": TERM_ID,
        "target_vi": TARGET,
    }

    persisted = json.loads((glossary / "canonical_findings.json").read_text(encoding="utf-8"))
    suggestions = persisted["findings"][0]["suggested_targets_vi"]
    assert TARGET in suggestions


def test_cooking_points_alias_is_not_canonicalized_outside_localize_source(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True

    finding = refresh_canonical_resolutions(
        tmp_path,
        {"schema_version": 1, "policy": {"canonical": False}, "findings": [_finding("text_data_dict.json")]},
    )["findings"][0]
    assert finding["review_resolution"] == {
        "decision_id": DECISION_ID,
        "action": "lock",
        "target_vi": TARGET,
    }
    assert finding["canonical_resolution"] is None

import json
from pathlib import Path

from scripts.canonical_findings import refresh_canonical_resolutions
from scripts.harden_character0146_scout_finding import ALIAS, DECISION_ID, TARGET, TERM_ID, harden


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _finding(key: str = "Character0146", source_path: str = "localize_dict.json") -> dict:
    return {
        "finding_id": "cf-3caafd7a2224e00e",
        "status": "open",
        "source_zh_cn": ALIAS,
        "match_mode": "exact",
        "source_paths": [source_path],
        "key_exact": [key],
        "json_path_prefixes": [],
        "kinds": ["system_label"],
        "concepts": ["Prize pool UI label"],
        "suggested_targets_vi": [],
        "confidence_levels": ["high"],
        "reasons": ["Reusable label requires canonical identity."],
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
    return glossary


def test_hardener_is_idempotent_and_resolves_exact_character_key(tmp_path: Path) -> None:
    glossary = _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    community = json.loads((glossary / "ui_community_terms.json").read_text(encoding="utf-8"))
    term = next(item for item in community["terms"] if item["id"] == TERM_ID)
    assert term["preferred"] == TARGET
    assert term["source_paths"] == ["localize_dict.json"]
    assert term["key_exact"] == ["Character0146"]
    assert term["match_mode"] == "exact"
    assert "Kho quà" in term["forbidden"]

    finding = refresh_canonical_resolutions(
        tmp_path,
        {"schema_version": 1, "policy": {"canonical": False}, "findings": [_finding()]},
    )["findings"][0]
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


def test_generic_pool_elsewhere_is_not_canonicalized(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    for finding in (_finding("Character9999"), _finding("Character0146", "text_data_dict.json")):
        resolved = refresh_canonical_resolutions(
            tmp_path,
            {"schema_version": 1, "policy": {"canonical": False}, "findings": [finding]},
        )["findings"][0]
        assert resolved["canonical_resolution"] is None

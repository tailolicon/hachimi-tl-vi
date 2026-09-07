import json
from pathlib import Path

from scripts.canonical_findings import refresh_canonical_resolutions
from scripts.harden_support_unique_effect_label_finding import (
    ALIAS,
    DECISION_ID,
    REVIEWED_TERM_ID,
    TARGET,
    TERM_ID,
    harden,
)


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _finding(
    source_text: str = ALIAS,
    key: str = "Character0050",
    source_path: str = "localize_dict.json",
) -> dict:
    return {
        "finding_id": "cf-5cc239af1c9d7710",
        "status": "open",
        "source_zh_cn": ALIAS,
        "match_mode": "contains",
        "source_paths": [source_path],
        "key_exact": [key],
        "json_path_prefixes": [],
        "kinds": ["system_label"],
        "concepts": ["Support-card Unique Effect label"],
        "suggested_targets_vi": [],
        "confidence_levels": ["high"],
        "reasons": ["Reusable support-card UI label requires canonical identity."],
        "evidence_count": 1,
        "evidence": [{"source_text": source_text}],
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


def test_hardener_is_idempotent_and_resolves_known_localize_keys(tmp_path: Path) -> None:
    glossary = _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    community = json.loads((glossary / "ui_community_terms.json").read_text(encoding="utf-8"))
    term = next(item for item in community["terms"] if item["id"] == TERM_ID)
    assert term["preferred"] == TARGET
    assert term["source_paths"] == ["localize_dict.json"]
    assert term["key_exact"] == ["Character0050", "Character0196"]
    assert term["match_mode"] == "contains"
    assert "Bonus riêng" in term["forbidden"]

    reviews = json.loads((glossary / "terminology_reviews.json").read_text(encoding="utf-8"))
    decision = next(item for item in reviews["decisions"] if item["decision_id"] == DECISION_ID)
    assert decision["term_id"] == REVIEWED_TERM_ID
    assert decision["target_vi"] == TARGET
    assert decision["source_paths"] == ["localize_dict.json"]
    assert decision["key_exact"] == ["Character0050", "Character0196"]
    assert decision["match_mode"] == "contains"

    for finding in (_finding(), _finding("固有加成详情", "Character0196")):
        resolved = refresh_canonical_resolutions(
            tmp_path,
            {"schema_version": 1, "policy": {"canonical": False}, "findings": [finding]},
        )["findings"][0]
        assert resolved["review_resolution"] == {
            "decision_id": DECISION_ID,
            "action": "lock",
            "target_vi": TARGET,
        }
        assert resolved["canonical_resolution"] == {
            "layer": "community",
            "term_id": TERM_ID,
            "target_vi": TARGET,
        }


def test_hardener_migrates_stale_reviewed_registry_term(tmp_path: Path) -> None:
    glossary = _seed(tmp_path)
    _write(
        glossary / "term_registry.json",
        {
            "schema_version": 1,
            "terms": [
                {
                    "id": REVIEWED_TERM_ID,
                    "category": "system_label",
                    "zh_cn": [ALIAS],
                    "target_vi": "Hiệu ứng riêng",
                    "locked": True,
                    "review": {"decision_id": DECISION_ID, "source": "glossary/terminology_reviews.json"},
                }
            ],
        },
    )
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False
    registry = json.loads((glossary / "term_registry.json").read_text(encoding="utf-8"))
    term = registry["terms"][0]
    assert term["target_vi"] == TARGET
    assert term["source_paths"] == ["localize_dict.json"]
    assert term["key_exact"] == ["Character0050", "Character0196"]
    assert term["match_mode"] == "contains"


def test_scope_does_not_touch_named_unique_effects_or_unrelated_localize_keys(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    for finding in (
        _finding(key="Character9999"),
        _finding(source_path="text_data_dict.json", key="150"),
    ):
        resolved = refresh_canonical_resolutions(
            tmp_path,
            {"schema_version": 1, "policy": {"canonical": False}, "findings": [finding]},
        )["findings"][0]
        assert resolved["canonical_resolution"] is None

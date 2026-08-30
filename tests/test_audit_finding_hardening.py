from __future__ import annotations

import json
from pathlib import Path

from scripts.harden_audit_findings import NIGHT_OWL_REFERENCE_VARIANT, harden
from scripts.canonical_findings import refresh_canonical_resolutions


def test_hardener_is_idempotent_and_resolves_night_owl_reference_variant(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    (glossary / "ui_community_terms.json").write_text(
        json.dumps({"schema_version": 1, "terms": []}, ensure_ascii=False),
        encoding="utf-8",
    )
    (glossary / "term_registry.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "source_bridge_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "terminology_reviews.json").write_text(json.dumps({"decisions": []}), encoding="utf-8")

    finding = {
        "finding_id": "cf-test-night-owl-variant",
        "status": "open",
        "source_zh_cn": "熬夜倾向",
        "match_mode": "contains",
        "source_paths": ["text_data_dict.json"],
        "key_exact": [],
        "json_path_prefixes": [["143"]],
        "suggested_targets_vi": ["Night Owl"],
        "canonical_resolution": None,
        "review_resolution": None,
    }
    ledger = {"schema_version": 1, "findings": [finding]}

    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    payload = json.loads((glossary / "ui_community_terms.json").read_text(encoding="utf-8"))
    rule = next(item for item in payload["terms"] if item["id"] == NIGHT_OWL_REFERENCE_VARIANT["id"])
    assert rule["source_aliases"] == ["熬夜倾向"]
    assert rule["preferred"] == "Night Owl"
    assert rule["json_path_prefixes"] == [["143"]]

    refreshed = refresh_canonical_resolutions(tmp_path, ledger)
    resolution = refreshed["findings"][0]["canonical_resolution"]
    assert resolution == {
        "layer": "community",
        "term_id": "common.condition.night_owl.reference_variant",
        "target_vi": "Night Owl",
    }


def test_night_owl_reference_variant_does_not_resolve_outside_category_143(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    (glossary / "ui_community_terms.json").write_text(
        json.dumps({"schema_version": 1, "terms": []}, ensure_ascii=False),
        encoding="utf-8",
    )
    (glossary / "term_registry.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "source_bridge_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "terminology_reviews.json").write_text(json.dumps({"decisions": []}), encoding="utf-8")

    assert harden(tmp_path) is True

    ledger = {
        "schema_version": 1,
        "findings": [
            {
                "finding_id": "cf-test-night-owl-prose",
                "status": "open",
                "source_zh_cn": "熬夜倾向",
                "match_mode": "contains",
                "source_paths": ["text_data_dict.json"],
                "key_exact": [],
                "json_path_prefixes": [["999"]],
                "suggested_targets_vi": ["Night Owl"],
                "canonical_resolution": None,
                "review_resolution": None,
            }
        ],
    }

    refreshed = refresh_canonical_resolutions(tmp_path, ledger)
    assert refreshed["findings"][0]["canonical_resolution"] is None

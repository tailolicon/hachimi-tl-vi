from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import refresh_canonical_resolutions
from scripts.harden_aoharu_ignited_spirit_finding import FAMILY_RULE, VARIANTS, harden


def _write(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _seed(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    _write(glossary / "ui_community_terms.json", {"schema_version": 1, "terms": []})
    _write(glossary / "terminology_reviews.json", {"schema_version": 1, "decisions": []})
    _write(glossary / "term_registry.json", {"terms": []})
    _write(glossary / "source_bridge_terms.json", {"terms": []})
    _write(glossary / "skill_name_style.json", {"canonical_examples": []})
    _write(glossary / "canonical_findings.json", {
        "schema_version": 1,
        "findings": [{
            "finding_id": "cf-d3dd61a3ce1f7dd6",
            "status": "open",
            "source_zh_cn": "点燃青春",
            "match_mode": "contains",
            "source_paths": ["text_data_dict.json"],
            "key_exact": [],
            "json_path_prefixes": [["147"]],
            "suggested_targets_vi": [],
            "canonical_resolution": None,
            "review_resolution": None,
        }],
    })


def test_hardener_locks_global_ignited_spirit_family_and_is_idempotent(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    community = json.loads((tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8"))
    family = next(term for term in community["terms"] if term["id"] == FAMILY_RULE["id"])
    assert family["preferred"] == "Ignited Spirit"
    assert family["json_path_prefixes"] == [["147"]]
    assert family["match_mode"] == "contains"

    reviews = json.loads((tmp_path / "glossary" / "terminology_reviews.json").read_text(encoding="utf-8"))
    by_source = {row["source_zh_cn"]: row for row in reviews["decisions"] if row.get("action") == "lock"}
    assert by_source["点燃青春"]["target_vi"] == "Ignited Spirit"
    for source, target, jp in VARIANTS:
        assert by_source[source]["target_vi"] == target
        assert by_source[source]["ja"] == [jp]
        assert by_source[source]["match_mode"] == "exact"


def test_finding_resolves_only_inside_skill_title_category(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    ledger = json.loads((tmp_path / "glossary" / "canonical_findings.json").read_text(encoding="utf-8"))
    finding = refresh_canonical_resolutions(tmp_path, ledger)["findings"][0]
    assert finding["review_resolution"]["target_vi"] == "Ignited Spirit"
    assert finding["canonical_resolution"] == {
        "layer": "community",
        "term_id": "skill.aoharu.ignited_spirit.family",
        "target_vi": "Ignited Spirit",
    }

    outside = dict(finding)
    outside["canonical_resolution"] = None
    outside["review_resolution"] = None
    outside["json_path_prefixes"] = [["16"]]
    refreshed = refresh_canonical_resolutions(tmp_path, {"schema_version": 1, "findings": [outside]})["findings"][0]
    assert refreshed["canonical_resolution"] is None

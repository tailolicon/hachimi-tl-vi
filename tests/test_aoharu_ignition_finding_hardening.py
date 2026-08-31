from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import refresh_canonical_resolutions
from scripts.harden_aoharu_ignition_finding import AOHARU_IGNITION, harden
from scripts.translation_review_common import community_term_matches


def _write(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _seed(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    _write(glossary / "ui_community_terms.json", {"schema_version": 1, "terms": []})
    _write(glossary / "term_registry.json", {"terms": []})
    _write(glossary / "source_bridge_terms.json", {"terms": []})
    _write(glossary / "terminology_reviews.json", {"decisions": []})
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


def test_hardener_adds_scoped_ignition_family_and_is_idempotent(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    community = json.loads((tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8"))
    rule = next(term for term in community["terms"] if term["id"] == AOHARU_IGNITION["id"])
    assert rule["preferred"] == "Thắp lửa thanh xuân"
    assert rule["forbidden"] == ["Bùng cháy thanh xuân"]
    assert rule["source_paths"] == ["text_data_dict.json"]
    assert rule["json_path_prefixes"] == [["147"]]
    assert rule["match_mode"] == "contains"

    finding = json.loads((tmp_path / "glossary" / "canonical_findings.json").read_text(encoding="utf-8"))["findings"][0]
    assert finding["suggested_targets_vi"] == ["Thắp lửa thanh xuân"]


def test_ignition_rule_accepts_its_family_and_rejects_combustion_wording(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    terms = json.loads((tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8"))["terms"]

    good = community_term_matches(
        None,
        "点燃青春・速＋",
        "Thắp lửa thanh xuân・Tốc độ＋",
        terms,
        source_path="text_data_dict.json",
        json_path=["147", "2102101"],
    )
    bad = community_term_matches(
        None,
        "点燃青春・速＋",
        "Bùng cháy thanh xuân・Tốc độ＋",
        terms,
        source_path="text_data_dict.json",
        json_path=["147", "2102101"],
    )
    unrelated = community_term_matches(
        None,
        "燃烧青春・速",
        "Bùng cháy thanh xuân・Tốc độ",
        terms,
        source_path="text_data_dict.json",
        json_path=["147", "2101101"],
    )
    assert good and good[0]["accepted_present"] is True and good[0]["forbidden_present"] is False
    assert bad and bad[0]["forbidden_present"] is True
    assert unrelated == []


def test_finding_resolves_to_aoharu_ignition_family(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    ledger = json.loads((tmp_path / "glossary" / "canonical_findings.json").read_text(encoding="utf-8"))
    finding = refresh_canonical_resolutions(tmp_path, ledger)["findings"][0]
    assert finding["canonical_resolution"] == {
        "layer": "community",
        "term_id": "skill.aoharu_ignition.family",
        "target_vi": "Thắp lửa thanh xuân",
    }

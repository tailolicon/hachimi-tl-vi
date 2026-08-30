from __future__ import annotations

import json
from pathlib import Path

from scripts.harden_audit_findings import (
    EPIPHANEIA_NO_HOLDING_BACK_CONDITION,
    JUNIOR_MAKE_DEBUT,
    MENTAL_GUARD_CONDITION,
    MOXIE_SKILL,
    NIGHT_OWL_REFERENCE_VARIANT,
    RECOVERY_SPIRIT_CONDITION,
    SCHOLAR_CONDITION,
    harden,
)
from scripts.canonical_findings import refresh_canonical_resolutions


def _seed_glossary(tmp_path: Path) -> Path:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    (glossary / "ui_community_terms.json").write_text(
        json.dumps({"schema_version": 1, "terms": []}, ensure_ascii=False),
        encoding="utf-8",
    )
    (glossary / "term_registry.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "source_bridge_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "terminology_reviews.json").write_text(json.dumps({"decisions": []}), encoding="utf-8")
    return glossary


def _finding(source: str, category: str = "142") -> dict[str, object]:
    return {
        "finding_id": f"cf-test-{source}-{category}",
        "status": "open",
        "source_zh_cn": source,
        "match_mode": "exact",
        "source_paths": ["text_data_dict.json"],
        "key_exact": [],
        "json_path_prefixes": [[category]],
        "suggested_targets_vi": [],
        "canonical_resolution": None,
        "review_resolution": None,
    }


def test_hardener_is_idempotent_and_resolves_night_owl_reference_variant(tmp_path: Path) -> None:
    glossary = _seed_glossary(tmp_path)
    ledger = {"schema_version": 1, "findings": [{**_finding("熬夜倾向", "143"), "match_mode": "contains"}]}
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False
    payload = json.loads((glossary / "ui_community_terms.json").read_text(encoding="utf-8"))
    rule = next(item for item in payload["terms"] if item["id"] == NIGHT_OWL_REFERENCE_VARIANT["id"])
    assert rule["source_aliases"] == ["熬夜倾向"]
    assert rule["preferred"] == "Night Owl"
    assert rule["json_path_prefixes"] == [["143"]]
    assert refresh_canonical_resolutions(tmp_path, ledger)["findings"][0]["canonical_resolution"] == {
        "layer": "community",
        "term_id": "common.condition.night_owl.reference_variant",
        "target_vi": "Night Owl",
    }


def test_night_owl_reference_variant_does_not_resolve_outside_category_143(tmp_path: Path) -> None:
    _seed_glossary(tmp_path)
    assert harden(tmp_path) is True
    ledger = {"schema_version": 1, "findings": [{**_finding("熬夜倾向", "999"), "match_mode": "contains"}]}
    assert refresh_canonical_resolutions(tmp_path, ledger)["findings"][0]["canonical_resolution"] is None


def test_junior_make_debut_resolves_the_scoped_audit_finding(tmp_path: Path) -> None:
    glossary = _seed_glossary(tmp_path)
    assert harden(tmp_path) is True
    community = json.loads((glossary / "ui_community_terms.json").read_text(encoding="utf-8"))
    rule = next(item for item in community["terms"] if item["id"] == JUNIOR_MAKE_DEBUT["id"])
    assert rule["key_exact"] == ["SingleMode619001"]
    ledger = {"schema_version": 1, "findings": [{
        "finding_id": "cf-test-junior-make-debut", "status": "open", "source_zh_cn": "新马级出道赛",
        "match_mode": "contains", "source_paths": ["localize_dict.json"], "key_exact": ["SingleMode619001"],
        "json_path_prefixes": [], "suggested_targets_vi": [], "canonical_resolution": None, "review_resolution": None,
    }]}
    finding = refresh_canonical_resolutions(tmp_path, ledger)["findings"][0]
    assert finding["review_resolution"]["target_vi"] == "Junior Make Debut"
    assert finding["canonical_resolution"]["target_vi"] == "Junior Make Debut"


def test_junior_make_debut_rule_does_not_resolve_another_localize_key(tmp_path: Path) -> None:
    _seed_glossary(tmp_path)
    assert harden(tmp_path) is True
    ledger = {"schema_version": 1, "findings": [{
        "finding_id": "cf-test-junior-wrong", "status": "open", "source_zh_cn": "新马级出道赛",
        "match_mode": "contains", "source_paths": ["localize_dict.json"], "key_exact": ["Story999999"],
        "json_path_prefixes": [], "suggested_targets_vi": [], "canonical_resolution": None, "review_resolution": None,
    }]}
    assert refresh_canonical_resolutions(tmp_path, ledger)["findings"][0]["canonical_resolution"] is None


def test_moxie_resolves_only_the_skill_title_category(tmp_path: Path) -> None:
    glossary = _seed_glossary(tmp_path)
    assert harden(tmp_path) is True
    community = json.loads((glossary / "ui_community_terms.json").read_text(encoding="utf-8"))
    rule = next(item for item in community["terms"] if item["id"] == MOXIE_SKILL["id"])
    assert rule["preferred"] == "Moxie"
    ledger = {"schema_version": 1, "findings": [_finding("随势而动", "147")]}
    finding = refresh_canonical_resolutions(tmp_path, ledger)["findings"][0]
    assert finding["review_resolution"]["target_vi"] == "Moxie"
    assert finding["canonical_resolution"]["target_vi"] == "Moxie"


def test_moxie_does_not_resolve_same_words_outside_skill_title_category(tmp_path: Path) -> None:
    _seed_glossary(tmp_path)
    assert harden(tmp_path) is True
    ledger = {"schema_version": 1, "findings": [_finding("随势而动", "163")]}
    assert refresh_canonical_resolutions(tmp_path, ledger)["findings"][0]["canonical_resolution"] is None


def test_trainer_ability_conditions_resolve_in_category_142(tmp_path: Path) -> None:
    glossary = _seed_glossary(tmp_path)
    assert harden(tmp_path) is True
    community = json.loads((glossary / "ui_community_terms.json").read_text(encoding="utf-8"))
    by_id = {item["id"]: item for item in community["terms"]}
    expected = (
        (SCHOLAR_CONDITION, "勤勉好学", "Scholar"),
        (MENTAL_GUARD_CONDITION, "精神防护", "Mental Guard"),
        (RECOVERY_SPIRIT_CONDITION, "恢复精神", "Recovery Spirit"),
    )
    for rule, source, target in expected:
        assert by_id[rule["id"]]["preferred"] == target
        finding = refresh_canonical_resolutions(tmp_path, {"schema_version": 1, "findings": [_finding(source)]})["findings"][0]
        assert finding["review_resolution"]["target_vi"] == target
        assert finding["canonical_resolution"]["target_vi"] == target


def test_trainer_ability_condition_words_do_not_resolve_outside_category_142(tmp_path: Path) -> None:
    _seed_glossary(tmp_path)
    assert harden(tmp_path) is True
    for source in ("勤勉好学", "精神防护", "恢复精神"):
        finding = refresh_canonical_resolutions(tmp_path, {"schema_version": 1, "findings": [_finding(source, "163")]})["findings"][0]
        assert finding["canonical_resolution"] is None


def test_epiphaneia_no_holding_back_condition_resolves_only_category_142(tmp_path: Path) -> None:
    glossary = _seed_glossary(tmp_path)
    assert harden(tmp_path) is True
    community = json.loads((glossary / "ui_community_terms.json").read_text(encoding="utf-8"))
    rule = next(item for item in community["terms"] if item["id"] == EPIPHANEIA_NO_HOLDING_BACK_CONDITION["id"])
    assert rule["source_aliases"] == ["传至双腿的焦躁"]
    assert rule["preferred"] == "I Won't Hold Back!!"
    assert rule["json_path_prefixes"] == [["142"]]
    finding = refresh_canonical_resolutions(tmp_path, {"schema_version": 1, "findings": [_finding("传至双腿的焦躁")]})["findings"][0]
    assert finding["review_resolution"] == {
        "decision_id": "audit.finding.condition-epiphaneia-no-holding-back",
        "action": "lock",
        "target_vi": "I Won't Hold Back!!",
    }
    assert finding["canonical_resolution"] == {
        "layer": "community",
        "term_id": "condition.epiphaneia.no_holding_back",
        "target_vi": "I Won't Hold Back!!",
    }


def test_epiphaneia_no_holding_back_words_do_not_resolve_as_generic_prose(tmp_path: Path) -> None:
    _seed_glossary(tmp_path)
    assert harden(tmp_path) is True
    finding = refresh_canonical_resolutions(tmp_path, {"schema_version": 1, "findings": [_finding("传至双腿的焦躁", "163")]})["findings"][0]
    assert finding["canonical_resolution"] is None

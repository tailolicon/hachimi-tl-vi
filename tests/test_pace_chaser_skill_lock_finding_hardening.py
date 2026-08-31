from __future__ import annotations

import json
from pathlib import Path

from scripts.apply_terminology_reviews import apply_reviews
from scripts.canonical_findings import refresh_canonical_resolutions
from scripts.harden_pace_chaser_skill_lock_finding import harden
from scripts.translation_review_common import community_term_matches, locked_term_matches


def _write(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _seed(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    _write(glossary / "ui_community_terms.json", {
        "terms": [{
            "id": "common.style.pace_chaser",
            "category": "running_style",
            "source_aliases": ["先行"],
            "preferred": "Pace Chaser",
            "accepted": ["Pace Chaser"],
            "compact": ["Pace"],
            "forbidden": ["Senko"],
            "require_accepted": True,
        }]
    })
    _write(glossary / "term_registry.json", {
        "terms": [
            {
                "id": "reviewed.skill_name.f8f77efa84ec",
                "category": "skill_name",
                "zh_cn": ["先行牵制"],
                "target_vi": "Kiềm chế Senko",
                "locked": True,
            },
            {
                "id": "reviewed.skill_name.ff328aef1290",
                "category": "skill_name",
                "zh_cn": ["先行直线○"],
                "target_vi": "Đường thẳng Senko ○",
                "locked": True,
            },
            {
                "id": "reviewed.skill_name.unrelated",
                "category": "skill_name",
                "zh_cn": ["其他技能"],
                "target_vi": "Senko",
                "locked": True,
            },
        ]
    })
    _write(glossary / "source_bridge_terms.json", {"terms": []})
    _write(glossary / "skill_name_style.json", {"canonical_examples": []})
    _write(glossary / "terminology_reviews.json", {"decisions": [
        {
            "decision_id": "pace-control",
            "term_id": "reviewed.skill_name.f8f77efa84ec",
            "source_zh_cn": "先行牵制",
            "target_vi": "Kiềm chế Senko",
            "action": "lock",
            "kind": "skill_name",
            "category": "skill_name",
        },
        {
            "decision_id": "unrelated",
            "term_id": "reviewed.skill_name.unrelated",
            "source_zh_cn": "其他技能",
            "target_vi": "Senko",
            "action": "lock",
            "kind": "skill_name",
            "category": "skill_name",
        },
    ]})
    _write(glossary / "canonical_findings.json", {
        "schema_version": 1,
        "findings": [{
            "finding_id": "cf-f57d921afca6a993",
            "status": "open",
            "source_zh_cn": "先行",
            "match_mode": "contains",
            "source_paths": ["text_data_dict.json"],
            "key_exact": [],
            "json_path_prefixes": [],
            "suggested_targets_vi": [],
            "canonical_resolution": None,
            "review_resolution": None,
        }],
    })


def test_hardener_migrates_review_source_and_generated_legacy_senko_locks(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    reviews = json.loads((tmp_path / "glossary" / "terminology_reviews.json").read_text(encoding="utf-8"))
    decisions = {decision["decision_id"]: decision for decision in reviews["decisions"]}
    assert decisions["pace-control"]["target_vi"] == "Kiềm chế Pace Chaser"
    assert decisions["unrelated"]["target_vi"] == "Senko"

    registry = json.loads((tmp_path / "glossary" / "term_registry.json").read_text(encoding="utf-8"))
    by_id = {term["id"]: term for term in registry["terms"]}
    assert by_id["reviewed.skill_name.f8f77efa84ec"]["target_vi"] == "Kiềm chế Pace Chaser"
    assert by_id["reviewed.skill_name.ff328aef1290"]["target_vi"] == "Đường thẳng Pace Chaser ○"
    assert by_id["reviewed.skill_name.unrelated"]["target_vi"] == "Senko"

    # The migrated review source must now be safely re-applicable; this is the
    # ordering failure that previously broke every later context Sync.
    reapplied, _ = apply_reviews(registry, reviews)
    assert next(term for term in reapplied["terms"] if term["id"] == "reviewed.skill_name.f8f77efa84ec")["target_vi"] == "Kiềm chế Pace Chaser"

    finding = json.loads((tmp_path / "glossary" / "canonical_findings.json").read_text(encoding="utf-8"))["findings"][0]
    assert finding["suggested_targets_vi"] == ["Pace Chaser"]


def test_migrated_skill_lock_and_running_style_rule_are_compatible(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    registry = json.loads((tmp_path / "glossary" / "term_registry.json").read_text(encoding="utf-8"))
    community = json.loads((tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8"))

    target = "Kiềm chế Pace Chaser"
    locked = locked_term_matches(
        "先行牵制", target, registry["terms"],
        source_path="text_data_dict.json", json_path=["147", "2008601"],
    )
    common = community_term_matches(
        None, "先行牵制", target, community["terms"],
        source_path="text_data_dict.json", json_path=["147", "2008601"],
    )
    assert locked and locked[0]["present"] is True
    assert common and common[0]["accepted_present"] is True
    assert common[0]["forbidden_present"] is False


def test_finding_resolves_to_existing_pace_chaser_canon_after_hardening(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    ledger = json.loads((tmp_path / "glossary" / "canonical_findings.json").read_text(encoding="utf-8"))
    finding = refresh_canonical_resolutions(tmp_path, ledger)["findings"][0]
    assert finding["canonical_resolution"] == {
        "layer": "community",
        "term_id": "common.style.pace_chaser",
        "target_vi": "Pace Chaser",
    }

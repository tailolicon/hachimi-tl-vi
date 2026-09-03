from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import active_findings, refresh_canonical_resolutions
from scripts.harden_mental_strength_phrase_finding import POWER_TERM_ID, TERM_ID, harden
from scripts.translation_review_common import community_term_matches, load_community_terms


def _write_terms(root: Path) -> None:
    glossary = root / "glossary"
    glossary.mkdir(parents=True)
    (glossary / "ui_community_terms.json").write_text(
        json.dumps(
            {
                "terms": [
                    {
                        "id": POWER_TERM_ID,
                        "category": "stat",
                        "source_aliases": ["パワー", "力量"],
                        "preferred": "Power",
                        "accepted": ["Power"],
                        "forbidden": ["Sức mạnh"],
                        "require_accepted": True,
                    }
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def test_mental_strength_exact_phrase_beats_power_substring_without_overmatching(tmp_path: Path) -> None:
    _write_terms(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False
    terms = load_community_terms(tmp_path)

    exact = community_term_matches(
        None,
        "精神力量",
        "Sức mạnh tinh thần",
        terms,
        source_path="text_data_dict.json",
        json_path=["147", "3100801"],
    )
    longer = community_term_matches(
        None,
        "精神力量很重要",
        "Sức mạnh tinh thần rất quan trọng",
        terms,
        source_path="text_data_dict.json",
        json_path=["147", "999"],
    )
    stat = community_term_matches(
        None,
        "力量",
        "Power",
        terms,
        source_path="text_data_dict.json",
        json_path=["172", "1"],
    )

    assert [row["id"] for row in exact] == [TERM_ID]
    assert exact[0]["preferred"] == "Sức mạnh tinh thần"
    assert longer == []
    assert stat[0]["id"] == POWER_TERM_ID
    assert stat[0]["preferred"] == "Power"


def test_mental_strength_rule_resolves_original_source_path_scoped_finding(tmp_path: Path) -> None:
    _write_terms(tmp_path)
    assert harden(tmp_path) is True
    glossary = tmp_path / "glossary"
    for name, payload in (
        ("terminology_reviews.json", {"decisions": []}),
        ("term_registry.json", {"terms": []}),
        ("source_bridge_terms.json", {"terms": []}),
        ("skill_name_style.json", {"canonical_examples": []}),
    ):
        (glossary / name).write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    ledger = {
        "schema_version": 1,
        "findings": [
            {
                "finding_id": "cf-1fb0ec7c1c77dfb1",
                "status": "open",
                "source_zh_cn": "精神力量",
                "match_mode": "exact",
                "source_paths": ["text_data_dict.json"],
                "key_exact": [],
                "json_path_prefixes": [],
                "suggested_targets_vi": ["Sức mạnh tinh thần"],
                "canonical_resolution": None,
                "review_resolution": None,
            }
        ],
    }
    refreshed = refresh_canonical_resolutions(tmp_path, ledger)
    finding = refreshed["findings"][0]

    assert finding["canonical_resolution"] == {
        "layer": "community",
        "term_id": TERM_ID,
        "target_vi": "Sức mạnh tinh thần",
    }
    assert active_findings(refreshed) == []

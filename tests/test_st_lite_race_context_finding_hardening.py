from __future__ import annotations

import json
from pathlib import Path

from scripts.harden_saint_lite_race_context_finding import EXCLUSION, TERM_ID, harden
from scripts.resolve_context_guard_findings import resolve
from scripts.translation_review_common import load_locked_terms, locked_term_matches

FINDING_ID = "cf-6b9b893796ef90b5"
RACE_TERM_ID = "race.st_lite_kinen"


def _write(root: Path) -> None:
    glossary = root / "glossary"
    glossary.mkdir(parents=True)
    (glossary / "term_registry.json").write_text(
        json.dumps({
            "terms": [
                {
                    "id": TERM_ID,
                    "category": "character",
                    "zh_cn": ["圣列特", "圣烈特", "圣赖特"],
                    "target_vi": "Saint Lite",
                    "locked": True,
                },
                {
                    "id": RACE_TERM_ID,
                    "category": "race_name",
                    "zh_cn": ["圣列特纪念"],
                    "target_vi": "St. Lite Kinen",
                    "locked": True,
                    "source_paths": ["text_data_dict.json"],
                    "json_path_prefixes": [["111"]],
                    "match_mode": "contains",
                },
            ]
        }, ensure_ascii=False),
        encoding="utf-8",
    )
    (glossary / "ui_community_terms.json").write_text(
        json.dumps({"schema_version": 1, "terms": []}),
        encoding="utf-8",
    )
    (glossary / "canonical_findings.json").write_text(
        json.dumps({
            "findings": [{
                "finding_id": FINDING_ID,
                "status": "open",
                "source_zh_cn": "圣列特纪念",
                "suggested_targets_vi": ["St. Lite Kinen"],
                "canonical_resolution": None,
                "evidence": [{
                    "source_path": "text_data_dict.json",
                    "json_path": ["111", "62"],
                    "source_text": "圣列特纪念",
                    "current_text": "St. Lite Kinen",
                }],
            }]
        }, ensure_ascii=False),
        encoding="utf-8",
    )


def test_saint_lite_character_alias_does_not_overmatch_st_lite_kinen(tmp_path: Path) -> None:
    _write(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    registry = json.loads((tmp_path / "glossary" / "term_registry.json").read_text(encoding="utf-8"))
    character = next(item for item in registry["terms"] if item["id"] == TERM_ID)
    assert EXCLUSION in character["exclude_source_contains"]

    terms = load_locked_terms(tmp_path)
    ordinary = locked_term_matches(
        "圣列特",
        "Saint Lite",
        terms,
        source_path="text_data_dict.json",
        json_path=["170", "9046"],
    )
    assert any(match["id"] == TERM_ID for match in ordinary)

    race = locked_term_matches(
        "圣列特纪念",
        "St. Lite Kinen",
        terms,
        source_path="text_data_dict.json",
        json_path=["111", "62"],
    )
    assert not any(match["id"] == TERM_ID for match in race)
    assert any(match["id"] == RACE_TERM_ID for match in race)

    assert resolve(tmp_path) is True
    assert resolve(tmp_path) is False
    payload = json.loads((tmp_path / "glossary" / "canonical_findings.json").read_text(encoding="utf-8"))
    assert payload["findings"][0]["canonical_resolution"] == {
        "layer": "context_guard",
        "term_id": TERM_ID,
        "target_vi": "St. Lite Kinen",
    }

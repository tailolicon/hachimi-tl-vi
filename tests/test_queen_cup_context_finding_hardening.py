from __future__ import annotations

import json
from pathlib import Path

from scripts.harden_queen_cup_context_finding import (
    EXCLUSION,
    QUEEN_ELIZABETH_EXCLUSION,
    TERM_ID,
    harden,
)
from scripts.resolve_context_guard_findings import resolve
from scripts.translation_review_common import load_locked_terms, locked_term_matches

FINDING_ID = "cf-15798cd76b70746c"
QUEEN_ELIZABETH_FINDING_ID = "cf-02cb6811d87107a6"
QUEEN_ELIZABETH_TERM_ID = "race.queen_elizabeth_ii_cup"


def _write(root: Path) -> None:
    glossary = root / "glossary"
    glossary.mkdir(parents=True)
    (glossary / "term_registry.json").write_text(
        json.dumps({
            "terms": [
                {
                    "id": TERM_ID,
                    "zh_cn": ["女王杯"],
                    "target_vi": "Queen Cup",
                    "locked": True,
                    "source_paths": ["text_data_dict.json"],
                    "match_mode": "contains",
                },
                {
                    "id": QUEEN_ELIZABETH_TERM_ID,
                    "zh_cn": ["伊丽莎白女王杯"],
                    "target_vi": "Queen Elizabeth II Cup",
                    "locked": True,
                    "source_paths": ["text_data_dict.json"],
                    "match_mode": "contains",
                },
            ]
        }, ensure_ascii=False),
        encoding="utf-8",
    )
    (glossary / "ui_community_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "canonical_findings.json").write_text(
        json.dumps({
            "findings": [
                {
                    "finding_id": FINDING_ID,
                    "status": "open",
                    "source_zh_cn": "女王杯",
                    "canonical_resolution": None,
                    "evidence": [{
                        "source_path": "text_data_dict.json",
                        "json_path": ["111", "175"],
                        "source_text": "TCK女王杯",
                        "current_text": "TCK Jo-o Hai",
                    }],
                },
                {
                    "finding_id": QUEEN_ELIZABETH_FINDING_ID,
                    "status": "open",
                    "source_zh_cn": "伊丽莎白女王杯",
                    "canonical_resolution": None,
                    "evidence": [{
                        "source_path": "text_data_dict.json",
                        "json_path": ["111", "194"],
                        "source_text": "伊丽莎白女王杯",
                        "current_text": "Queen Elizabeth II Cup",
                    }],
                },
            ]
        }, ensure_ascii=False),
        encoding="utf-8",
    )


def test_queen_cup_alias_is_excluded_inside_distinct_full_race_names(tmp_path: Path) -> None:
    _write(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    registry = json.loads((tmp_path / "glossary" / "term_registry.json").read_text(encoding="utf-8"))
    queen = next(item for item in registry["terms"] if item["id"] == TERM_ID)
    assert EXCLUSION in queen["exclude_source_contains"]
    assert QUEEN_ELIZABETH_EXCLUSION in queen["exclude_source_contains"]

    terms = load_locked_terms(tmp_path)
    ordinary = locked_term_matches(
        "女王杯",
        "Queen Cup",
        terms,
        source_path="text_data_dict.json",
        json_path=["111", "100"],
    )
    assert any(match["id"] == TERM_ID for match in ordinary)

    tck = locked_term_matches(
        "TCK女王杯",
        "TCK Jo-o Hai",
        terms,
        source_path="text_data_dict.json",
        json_path=["111", "175"],
    )
    assert not any(match["id"] == TERM_ID for match in tck)

    queen_elizabeth = locked_term_matches(
        "伊丽莎白女王杯",
        "Queen Elizabeth II Cup",
        terms,
        source_path="text_data_dict.json",
        json_path=["111", "194"],
    )
    assert not any(match["id"] == TERM_ID for match in queen_elizabeth)
    assert any(match["id"] == QUEEN_ELIZABETH_TERM_ID for match in queen_elizabeth)

    assert resolve(tmp_path) is True
    assert resolve(tmp_path) is False
    payload = json.loads((tmp_path / "glossary" / "canonical_findings.json").read_text(encoding="utf-8"))
    by_id = {item["finding_id"]: item for item in payload["findings"]}
    expected = {
        "layer": "context_guard",
        "term_id": TERM_ID,
        "target_vi": "Queen Cup",
    }
    assert by_id[FINDING_ID]["canonical_resolution"] == expected
    assert by_id[QUEEN_ELIZABETH_FINDING_ID]["canonical_resolution"] == expected

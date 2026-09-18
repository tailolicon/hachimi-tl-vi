from __future__ import annotations

import json
from pathlib import Path

from scripts.harden_mainichi_hai_context_finding import EXCLUSION, TERM_ID, harden
from scripts.resolve_context_guard_findings import resolve
from scripts.translation_review_common import load_locked_terms, locked_term_matches

FINDING_ID = "cf-082d75bb73b709c6"
DAILY_HAI_TERM_ID = "reviewed.race_name.3b5a9de8fcb3"


def _write(root: Path) -> None:
    glossary = root / "glossary"
    glossary.mkdir(parents=True)
    (glossary / "term_registry.json").write_text(
        json.dumps({
            "terms": [
                {
                    "id": TERM_ID,
                    "zh_cn": ["每日杯"],
                    "target_vi": "Mainichi Hai",
                    "locked": True,
                    "source_paths": ["text_data_dict.json"],
                    "match_mode": "contains",
                },
                {
                    "id": DAILY_HAI_TERM_ID,
                    "zh_cn": ["每日杯新马锦标"],
                    "target_vi": "Daily Hai Junior Stakes",
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
            "findings": [{
                "finding_id": FINDING_ID,
                "status": "open",
                "source_zh_cn": "每日杯新马锦标",
                "canonical_resolution": None,
                "evidence": [{
                    "source_path": "text_data_dict.json",
                    "json_path": ["111", "71"],
                    "source_text": "每日杯新马锦标",
                    "current_text": "Daily Hai Nisai Stakes",
                }],
            }]
        }, ensure_ascii=False),
        encoding="utf-8",
    )


def test_mainichi_hai_alias_is_excluded_inside_daily_hai_junior_stakes(tmp_path: Path) -> None:
    _write(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    registry = json.loads((tmp_path / "glossary" / "term_registry.json").read_text(encoding="utf-8"))
    mainichi = next(item for item in registry["terms"] if item["id"] == TERM_ID)
    assert EXCLUSION in mainichi["exclude_source_contains"]

    terms = load_locked_terms(tmp_path)
    ordinary = locked_term_matches(
        "每日杯",
        "Mainichi Hai",
        terms,
        source_path="text_data_dict.json",
        json_path=["111", "70"],
    )
    assert any(match["id"] == TERM_ID for match in ordinary)

    daily_hai = locked_term_matches(
        "每日杯新马锦标",
        "Daily Hai Junior Stakes",
        terms,
        source_path="text_data_dict.json",
        json_path=["111", "71"],
    )
    assert not any(match["id"] == TERM_ID for match in daily_hai)
    assert any(match["id"] == DAILY_HAI_TERM_ID for match in daily_hai)

    assert resolve(tmp_path) is True
    assert resolve(tmp_path) is False
    payload = json.loads((tmp_path / "glossary" / "canonical_findings.json").read_text(encoding="utf-8"))
    assert payload["findings"][0]["canonical_resolution"] == {
        "layer": "context_guard",
        "term_id": TERM_ID,
        "target_vi": "Mainichi Hai",
    }

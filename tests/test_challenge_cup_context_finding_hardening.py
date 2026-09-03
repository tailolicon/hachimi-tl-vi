from __future__ import annotations

import json
from pathlib import Path

from scripts.harden_challenge_cup_context_finding import EXCLUSION, TERM_ID, harden
from scripts.resolve_context_guard_findings import resolve
from scripts.translation_review_common import load_locked_terms, locked_term_matches

FINDING_ID = "cf-234800d40ef253ed"


def _write(root: Path) -> None:
    glossary = root / "glossary"
    glossary.mkdir(parents=True)
    (glossary / "term_registry.json").write_text(
        json.dumps({
            "terms": [{
                "id": TERM_ID,
                "zh_cn": ["挑战杯"],
                "target_vi": "Challenge Cup",
                "locked": True,
                "source_paths": ["text_data_dict.json"],
                "match_mode": "contains",
            }]
        }, ensure_ascii=False),
        encoding="utf-8",
    )
    (glossary / "ui_community_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "canonical_findings.json").write_text(
        json.dumps({
            "findings": [{
                "finding_id": FINDING_ID,
                "status": "open",
                "source_zh_cn": "挑战杯",
                "canonical_resolution": None,
                "evidence": [{
                    "source_path": "text_data_dict.json",
                    "json_path": ["32", "3066"],
                    "source_text": "德比伯爵挑战杯",
                    "current_text": "Lord Derby Challenge Trophy",
                }],
            }]
        }, ensure_ascii=False),
        encoding="utf-8",
    )


def test_challenge_cup_alias_is_excluded_only_inside_lord_derby_challenge_trophy(tmp_path: Path) -> None:
    _write(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    registry = json.loads((tmp_path / "glossary" / "term_registry.json").read_text(encoding="utf-8"))
    challenge = registry["terms"][0]
    assert EXCLUSION in challenge["exclude_source_contains"]

    terms = load_locked_terms(tmp_path)
    ordinary = locked_term_matches(
        "挑战杯",
        "Challenge Cup",
        terms,
        source_path="text_data_dict.json",
        json_path=["32", "3067"],
    )
    assert any(match["id"] == TERM_ID for match in ordinary)

    lord_derby = locked_term_matches(
        "德比伯爵挑战杯",
        "Lord Derby Challenge Trophy",
        terms,
        source_path="text_data_dict.json",
        json_path=["32", "3066"],
    )
    assert not any(match["id"] == TERM_ID for match in lord_derby)

    assert resolve(tmp_path) is True
    payload = json.loads((tmp_path / "glossary" / "canonical_findings.json").read_text(encoding="utf-8"))
    assert payload["findings"][0]["canonical_resolution"] == {
        "layer": "context_guard",
        "term_id": TERM_ID,
        "target_vi": "Challenge Cup",
    }

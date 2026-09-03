from __future__ import annotations

import json
from pathlib import Path

from scripts.harden_queen_cup_context_finding import EXCLUSION, TERM_ID, harden
from scripts.resolve_context_guard_findings import resolve
from scripts.translation_review_common import load_locked_terms, locked_term_matches

FINDING_ID = "cf-15798cd76b70746c"


def _write(root: Path) -> None:
    glossary = root / "glossary"
    glossary.mkdir(parents=True)
    (glossary / "term_registry.json").write_text(
        json.dumps({
            "terms": [{
                "id": TERM_ID,
                "zh_cn": ["女王杯"],
                "target_vi": "Queen Cup",
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
                "source_zh_cn": "女王杯",
                "canonical_resolution": None,
                "evidence": [{
                    "source_path": "text_data_dict.json",
                    "json_path": ["111", "175"],
                    "source_text": "TCK女王杯",
                    "current_text": "TCK Jo-o Hai",
                }],
            }]
        }, ensure_ascii=False),
        encoding="utf-8",
    )


def test_queen_cup_alias_is_excluded_only_inside_tck_jo_o_hai(tmp_path: Path) -> None:
    _write(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    registry = json.loads((tmp_path / "glossary" / "term_registry.json").read_text(encoding="utf-8"))
    queen = registry["terms"][0]
    assert EXCLUSION in queen["exclude_source_contains"]

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

    assert resolve(tmp_path) is True
    payload = json.loads((tmp_path / "glossary" / "canonical_findings.json").read_text(encoding="utf-8"))
    assert payload["findings"][0]["canonical_resolution"] == {
        "layer": "context_guard",
        "term_id": TERM_ID,
        "target_vi": "Queen Cup",
    }

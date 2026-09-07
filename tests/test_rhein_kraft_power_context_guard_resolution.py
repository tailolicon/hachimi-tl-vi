from __future__ import annotations

import json
from pathlib import Path

from scripts.harden_power_context_finding import TERM_ID, harden
from scripts.resolve_context_guard_findings import POWER_CONTEXT_GUARD_IDS, resolve
from scripts.translation_review_common import community_term_matches, load_community_terms

FINDING_ID = "cf-47c737cc38fc1f48"


def test_rhein_kraft_name_does_not_trigger_power_stat(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir(parents=True)
    (glossary / "ui_community_terms.json").write_text(
        json.dumps({"terms": [{
            "id": TERM_ID,
            "category": "stat",
            "source_aliases": ["力量"],
            "preferred": "Power",
            "accepted": ["Power"],
            "compact": [],
            "forbidden": ["Sức mạnh"],
            "require_accepted": True,
        }]}, ensure_ascii=False),
        encoding="utf-8",
    )
    (glossary / "term_registry.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "canonical_findings.json").write_text(
        json.dumps({"findings": [{
            "finding_id": FINDING_ID,
            "status": "open",
            "canonical_resolution": None,
            "evidence": [{
                "source_path": "text_data_dict.json",
                "json_path": ["14", "110902"],
                "source_text": "主线故事决胜服（莱茵力量）",
                "current_text": "Trang phục chiến thắng cốt truyện chính (Rhein Kraft)",
            }],
        }]}, ensure_ascii=False),
        encoding="utf-8",
    )

    assert harden(tmp_path) is True
    terms = load_community_terms(tmp_path)
    matches = community_term_matches(
        None,
        "主线故事决胜服（莱茵力量）",
        "Trang phục chiến thắng cốt truyện chính (Rhein Kraft)",
        terms,
        source_path="text_data_dict.json",
        json_path=["14", "110902"],
    )
    assert not any(match["id"] == TERM_ID for match in matches)

    stat_matches = community_term_matches(
        None,
        "力量",
        "Power",
        terms,
        source_path="text_data_dict.json",
        json_path=["172", "1"],
    )
    assert any(match["id"] == TERM_ID for match in stat_matches)

    assert FINDING_ID in POWER_CONTEXT_GUARD_IDS
    assert resolve(tmp_path) is True
    finding = json.loads((glossary / "canonical_findings.json").read_text(encoding="utf-8"))["findings"][0]
    assert finding["canonical_resolution"] == {
        "layer": "context_guard",
        "term_id": TERM_ID,
        "target_vi": "Power",
    }

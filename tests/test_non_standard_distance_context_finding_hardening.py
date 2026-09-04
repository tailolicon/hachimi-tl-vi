from __future__ import annotations

import json
from pathlib import Path

from scripts.harden_non_standard_distance_context_finding import (
    NON_STANDARD_ALIASES,
    STANDARD_DISTANCE_IDS,
    harden,
)
from scripts.resolve_context_guard_findings import resolve
from scripts.translation_review_common import load_locked_terms, locked_term_matches


FINDING_ID = "cf-8faece2c0770dea4"


def _seed(root: Path) -> None:
    glossary = root / "glossary"
    glossary.mkdir(parents=True)
    registry = {
        "schema_version": 2,
        "terms": [
            {
                "id": term_id,
                "category": "skill_name",
                "zh_cn": [f"根干距离{grade}"],
                "target_vi": target,
                "locked": True,
            }
            for term_id, target in STANDARD_DISTANCE_IDS.items()
            for grade in [target[-1]]
        ],
    }
    (glossary / "term_registry.json").write_text(json.dumps(registry, ensure_ascii=False), encoding="utf-8")
    (glossary / "ui_community_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "canonical_findings.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "findings": [
                    {
                        "finding_id": FINDING_ID,
                        "status": "open",
                        "source_zh_cn": "非根干距离○",
                        "match_mode": "exact",
                        "source_paths": ["text_data_dict.json"],
                        "json_path_prefixes": [["147"]],
                        "canonical_resolution": None,
                        "evidence": [
                            {
                                "source_path": "text_data_dict.json",
                                "json_path": ["147", "2001401"],
                                "source_text": "非根干距离○",
                                "current_text": "Cự ly không chuẩn○",
                            }
                        ],
                    }
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def test_hardener_is_idempotent_and_excludes_non_standard_family(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    payload = json.loads((tmp_path / "glossary" / "term_registry.json").read_text(encoding="utf-8"))
    for term in payload["terms"]:
        assert term["exclude_source_contains"] == NON_STANDARD_ALIASES

    locked = load_locked_terms(tmp_path)
    assert not any(
        match["id"] == "reviewed.skill_name.b10fa1bb5f44"
        for match in locked_term_matches(
            "非根干距离○",
            "Cự ly không chuẩn○",
            locked,
            source_path="text_data_dict.json",
            json_path=["147", "2001401"],
        )
    )
    assert any(
        match["id"] == "reviewed.skill_name.b10fa1bb5f44"
        for match in locked_term_matches(
            "根干距离○",
            "Cự ly tiêu chuẩn ○",
            locked,
            source_path="text_data_dict.json",
            json_path=["147", "200132"],
        )
    )

    assert resolve(tmp_path) is True
    findings = json.loads((tmp_path / "glossary" / "canonical_findings.json").read_text(encoding="utf-8"))
    assert findings["findings"][0]["canonical_resolution"] == {
        "layer": "context_guard",
        "term_id": "reviewed.skill_name.b10fa1bb5f44",
        "target_vi": "Cự ly tiêu chuẩn ○",
    }

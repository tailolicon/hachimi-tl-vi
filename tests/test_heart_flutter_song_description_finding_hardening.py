from __future__ import annotations

import json
from pathlib import Path

from scripts.harden_heart_flutter_song_description_finding import EXCLUSION, FINDING_ID, TERM_ID, harden
from scripts.resolve_context_guard_findings import resolve
from scripts.translation_review_common import load_locked_terms, locked_term_matches


CURRENT_TEXT = (
    "Một ca khúc tràn đầy dũng khí và hy vọng, như ngôi sao sáng nhất đang lao đi rực rỡ.\\n"
    "Linh cảm khiến tim rung động――đó chính là tín hiệu cuộc đua bắt đầu."
)
REGENERATED_FINDING_ID = "cf-7b678d0f1ed3e725"


def _write_registry(root: Path) -> None:
    glossary = root / "glossary"
    glossary.mkdir(parents=True, exist_ok=True)
    (glossary / "term_registry.json").write_text(
        json.dumps(
            {
                "terms": [
                    {
                        "id": TERM_ID,
                        "category": "skill_name",
                        "zh_cn": ["心动"],
                        "target_vi": "Nhịp tim rộn ràng",
                        "locked": True,
                    }
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def test_heart_flutter_hardener_preserves_skill_and_excludes_song_prose(tmp_path: Path) -> None:
    _write_registry(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    payload = json.loads((tmp_path / "glossary" / "term_registry.json").read_text(encoding="utf-8"))
    term = payload["terms"][0]
    assert EXCLUSION in term["exclude_source_contains"]

    terms = load_locked_terms(tmp_path)
    skill = locked_term_matches(
        "心动",
        "Nhịp tim rộn ràng",
        terms,
        source_path="text_data_dict.json",
        json_path=["147", "999999"],
    )
    song_description = locked_term_matches(
        EXCLUSION,
        CURRENT_TEXT,
        terms,
        source_path="text_data_dict.json",
        json_path=["128", "1025"],
    )

    assert skill[0]["id"] == TERM_ID
    assert song_description == []


def test_heart_flutter_finding_resolves_after_exclusion(tmp_path: Path) -> None:
    _write_registry(tmp_path)
    assert harden(tmp_path) is True
    glossary = tmp_path / "glossary"
    (glossary / "ui_community_terms.json").write_text('{"terms": []}\n', encoding="utf-8")
    (glossary / "canonical_findings.json").write_text(
        json.dumps(
            {
                "findings": [
                    {
                        "finding_id": finding_id,
                        "status": "open",
                        "source_zh_cn": EXCLUSION,
                        "canonical_resolution": None,
                        "evidence": [
                            {
                                "source_path": "text_data_dict.json",
                                "json_path": ["128", "1025"],
                                "source_text": EXCLUSION,
                                "current_text": CURRENT_TEXT,
                            }
                        ],
                    }
                    for finding_id in (FINDING_ID, REGENERATED_FINDING_ID)
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    assert resolve(tmp_path) is True
    payload = json.loads((glossary / "canonical_findings.json").read_text(encoding="utf-8"))
    for finding in payload["findings"]:
        assert finding["canonical_resolution"] == {
            "layer": "context_guard",
            "term_id": TERM_ID,
            "target_vi": "Nhịp tim rộn ràng",
        }

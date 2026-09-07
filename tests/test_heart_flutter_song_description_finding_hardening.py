from __future__ import annotations

import json
from pathlib import Path

from scripts.harden_heart_flutter_song_description_finding import (
    EXCLUSION,
    FINDING_ID,
    LONG_TERM_ID,
    SUPPORT_TITLE_EXCLUSION,
    SUPPORT_TITLE_FINDING_ID,
    TERM_ID,
    harden,
)
from scripts.resolve_context_guard_findings import resolve
from scripts.resolve_heart_flutter_support_title_finding import resolve as resolve_support_title
from scripts.translation_review_common import load_locked_terms, locked_term_matches


CURRENT_TEXT = (
    "Một ca khúc tràn đầy dũng khí và hy vọng, như ngôi sao sáng nhất đang lao đi rực rỡ.\\n"
    "Linh cảm khiến tim rung động――đó chính là tín hiệu cuộc đua bắt đầu."
)
SUPPORT_TITLE_CURRENT_TEXT = "Ký ức khiến tim rung động♪"
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
                    },
                    {
                        "id": LONG_TERM_ID,
                        "category": "skill_name",
                        "zh_cn": ["怦然心动"],
                        "target_vi": "Trái tim rung động",
                        "locked": True,
                    },
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def test_heart_flutter_hardener_preserves_skills_and_excludes_false_positives(tmp_path: Path) -> None:
    _write_registry(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    payload = json.loads((tmp_path / "glossary" / "term_registry.json").read_text(encoding="utf-8"))
    by_id = {term["id"]: term for term in payload["terms"]}
    assert EXCLUSION in by_id[TERM_ID]["exclude_source_contains"]
    assert SUPPORT_TITLE_EXCLUSION in by_id[TERM_ID]["exclude_source_contains"]
    assert SUPPORT_TITLE_EXCLUSION in by_id[LONG_TERM_ID]["exclude_source_contains"]

    terms = load_locked_terms(tmp_path)
    short_skill = locked_term_matches(
        "心动",
        "Nhịp tim rộn ràng",
        terms,
        source_path="text_data_dict.json",
        json_path=["147", "999999"],
    )
    long_skill = locked_term_matches(
        "怦然心动",
        "Trái tim rung động",
        terms,
        source_path="text_data_dict.json",
        json_path=["147", "999998"],
    )
    song_description = locked_term_matches(
        EXCLUSION,
        CURRENT_TEXT,
        terms,
        source_path="text_data_dict.json",
        json_path=["128", "1025"],
    )
    support_title = locked_term_matches(
        SUPPORT_TITLE_EXCLUSION,
        SUPPORT_TITLE_CURRENT_TEXT,
        terms,
        source_path="text_data_dict.json",
        json_path=["150", "20044"],
    )

    assert TERM_ID in {match["id"] for match in short_skill}
    assert LONG_TERM_ID in {match["id"] for match in long_skill}
    assert song_description == []
    assert support_title == []


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


def test_heart_flutter_support_title_finding_resolves_only_after_both_aliases_are_excluded(tmp_path: Path) -> None:
    _write_registry(tmp_path)
    glossary = tmp_path / "glossary"
    (glossary / "ui_community_terms.json").write_text('{"terms": []}\n', encoding="utf-8")
    (glossary / "canonical_findings.json").write_text(
        json.dumps(
            {
                "findings": [
                    {
                        "finding_id": SUPPORT_TITLE_FINDING_ID,
                        "status": "open",
                        "source_zh_cn": SUPPORT_TITLE_EXCLUSION,
                        "canonical_resolution": None,
                        "evidence": [
                            {
                                "source_path": "text_data_dict.json",
                                "json_path": ["150", "20044"],
                                "source_text": SUPPORT_TITLE_EXCLUSION,
                                "current_text": SUPPORT_TITLE_CURRENT_TEXT,
                            }
                        ],
                    }
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    assert resolve_support_title(tmp_path) is False
    assert harden(tmp_path) is True
    assert resolve_support_title(tmp_path) is True
    payload = json.loads((glossary / "canonical_findings.json").read_text(encoding="utf-8"))
    assert payload["findings"][0]["canonical_resolution"] == {
        "layer": "context_guard",
        "term_id": LONG_TERM_ID,
        "target_vi": "Trái tim rung động",
    }

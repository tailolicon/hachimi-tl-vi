from __future__ import annotations

import json
from pathlib import Path

from scripts.harden_gran_alegria_cheer_prose_finding import DECISION, SOURCE, TERM_ID, harden
from scripts.translation_review_common import locked_term_matches


def _write(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _seed(tmp_path: Path) -> None:
    _write(
        tmp_path / "glossary" / "term_registry.json",
        {
            "terms": [
                {
                    "id": TERM_ID,
                    "category": "character",
                    "zh_cn": ["放声欢呼"],
                    "target_vi": "Gran Alegria",
                    "locked": True,
                }
            ]
        },
    )
    _write(tmp_path / "glossary" / "terminology_reviews.json", {"schema_version": 1, "decisions": []})


def test_hardener_excludes_only_the_false_positive_sentence_and_is_idempotent(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    registry = json.loads((tmp_path / "glossary" / "term_registry.json").read_text(encoding="utf-8"))
    term = registry["terms"][0]
    assert term["exclude_source_contains"] == [SOURCE]

    prose_matches = locked_term_matches(
        SOURCE,
        "Xin tuyên bố với tất cả những ai sinh ra trong thời đại này —\\nNào, hãy reo hò thật lớn.",
        [term],
        source_path="text_data_dict.json",
        json_path=["128", "1151"],
    )
    assert prose_matches == []

    real_identity_matches = locked_term_matches(
        "[特雷森学园]放声欢呼",
        "[Học viện Tracen] Gran Alegria",
        [term],
        source_path="text_data_dict.json",
        json_path=["1", "1"],
    )
    assert real_identity_matches and real_identity_matches[0]["target_vi"] == "Gran Alegria"

    reviews = json.loads((tmp_path / "glossary" / "terminology_reviews.json").read_text(encoding="utf-8"))
    decision = next(item for item in reviews["decisions"] if item["decision_id"] == DECISION["decision_id"])
    assert decision["action"] == "ignore"
    assert decision["source_zh_cn"] == SOURCE

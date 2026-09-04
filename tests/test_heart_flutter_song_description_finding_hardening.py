from __future__ import annotations

import json
from pathlib import Path

from scripts.harden_heart_flutter_song_description_finding import EXCLUSION, TERM_ID, harden
from scripts.translation_review_common import load_locked_terms, locked_term_matches


def _write_registry(root: Path) -> None:
    glossary = root / "glossary"
    glossary.mkdir(parents=True)
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
        "Một ca khúc tràn đầy dũng khí và hy vọng, như ngôi sao sáng nhất đang lao đi rực rỡ.\\n"
        "Linh cảm khiến tim rung động――đó chính là tín hiệu cuộc đua bắt đầu.",
        terms,
        source_path="text_data_dict.json",
        json_path=["128", "1025"],
    )

    assert skill[0]["id"] == TERM_ID
    assert song_description == []

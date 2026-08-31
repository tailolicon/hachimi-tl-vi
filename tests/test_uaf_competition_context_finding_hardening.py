from __future__ import annotations

import json
from pathlib import Path

from scripts.harden_uaf_competition_context_finding import TERM_ID, harden
from scripts.resolve_context_guard_findings import resolve
from scripts.translation_review_common import load_locked_terms, locked_term_matches


SOURCE = (
    "决出No.1运动员赛马娘的\\n"
    "综合体育大会<color=#FF6D26>『U.A.F.』</color>开幕！\\n"
    "赛马娘们将在15种独特的比赛中\\n"
    "挑战自我极限，挥洒汗水！\\n"
    "运动员们的灵魂共鸣，请拭目以待！"
)


def _seed(root: Path) -> None:
    glossary = root / "glossary"
    glossary.mkdir(parents=True)
    (glossary / "term_registry.json").write_text(json.dumps({"terms": [{
        "id": TERM_ID,
        "zh_cn": ["比赛"],
        "target_vi": "Cuộc đua",
        "locked": True,
    }]}, ensure_ascii=False), encoding="utf-8")
    (glossary / "ui_community_terms.json").write_text(
        json.dumps({"terms": []}, ensure_ascii=False), encoding="utf-8"
    )
    (glossary / "canonical_findings.json").write_text(json.dumps({
        "schema_version": 1,
        "findings": [{
            "finding_id": "cf-552896cb4b769204",
            "status": "open",
            "source_zh_cn": "比赛",
            "canonical_resolution": None,
            "review_resolution": None,
            "evidence": [{
                "source_path": "text_data_dict.json",
                "json_path": ["120", "7"],
                "source_text": SOURCE,
                "current_text": "Các Mã Nương sẽ thử thách giới hạn qua 15 Cuộc đua độc đáo.",
            }],
        }],
    }, ensure_ascii=False), encoding="utf-8")


def test_uaf_sports_disciplines_do_not_match_generic_race(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False
    terms = load_locked_terms(tmp_path)

    assert locked_term_matches("目标比赛", "Cuộc đua mục tiêu", terms)[0]["id"] == TERM_ID
    assert locked_term_matches(
        SOURCE,
        "Các Mã Nương sẽ thử thách giới hạn qua 15 môn thi đấu độc đáo.",
        terms,
        source_path="text_data_dict.json",
        json_path=["120", "7"],
    ) == []

    assert resolve(tmp_path) is True
    assert resolve(tmp_path) is False
    payload = json.loads((tmp_path / "glossary" / "canonical_findings.json").read_text(encoding="utf-8"))
    assert payload["findings"][0]["canonical_resolution"] == {
        "layer": "context_guard",
        "term_id": TERM_ID,
        "target_vi": "Cuộc đua",
    }

from __future__ import annotations

import json
from pathlib import Path

from scripts.harden_uaf_competition_context_finding import harden
from scripts.resolve_context_guard_findings import resolve
from scripts.translation_review_common import load_locked_terms, locked_term_matches


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _seed(tmp_path: Path) -> None:
    _write(tmp_path / "glossary" / "ui_community_terms.json", {"terms": []})
    _write(tmp_path / "glossary" / "term_registry.json", {"terms": [{
        "id": "race.generic",
        "zh_cn": ["比赛"],
        "target_vi": "Cuộc đua",
        "locked": True,
        "match_mode": "contains",
    }]})
    _write(tmp_path / "glossary" / "canonical_findings.json", {"findings": [{
        "finding_id": "cf-2b8709d527abc360",
        "status": "open",
        "source_zh_cn": "比赛",
        "canonical_resolution": None,
        "review_resolution": None,
        "evidence": [{
            "source_path": "text_data_dict.json",
            "json_path": ["120", "7"],
            "source_text": "赛马娘们将在15种独特的比赛中\\n挑战自我极限，挥洒汗水！",
            "current_text": "Các Mã Nương sẽ thử thách giới hạn bản thân qua 15 môn thi đấu độc đáo!",
        }],
    }]})


def test_uaf_sports_competition_resolves_without_disabling_generic_race(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False
    assert resolve(tmp_path) is True
    assert resolve(tmp_path) is False

    payload = json.loads((tmp_path / "glossary" / "canonical_findings.json").read_text(encoding="utf-8"))
    finding = payload["findings"][0]
    assert finding["canonical_resolution"] == {
        "layer": "context_guard",
        "term_id": "race.generic",
        "target_vi": "Cuộc đua",
    }

    terms = load_locked_terms(tmp_path)
    uaf = locked_term_matches(
        "赛马娘们将在15种独特的比赛中挑战自我极限",
        "Các Mã Nương sẽ thi đấu ở 15 môn thể thao độc đáo",
        terms,
        source_path="text_data_dict.json",
        json_path=["120", "7"],
    )
    assert not any(match["id"] == "race.generic" for match in uaf)

    race = locked_term_matches(
        "下一场比赛即将开始",
        "Cuộc đua tiếp theo sắp bắt đầu",
        terms,
        source_path="text_data_dict.json",
        json_path=["131", "999"],
    )
    generic = next(match for match in race if match["id"] == "race.generic")
    assert generic["present"] is True

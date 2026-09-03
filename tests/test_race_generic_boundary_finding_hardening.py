from __future__ import annotations

import json
from pathlib import Path

from scripts.harden_race_generic_boundary_finding import TERM_ID, harden
from scripts.resolve_context_guard_findings import resolve
from scripts.translation_review_common import load_locked_terms, locked_term_matches

FINDING_ID = "cf-187d58b59b5dc9be"


def test_generic_race_does_not_cross_derby_umamusume_boundary(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir(parents=True)
    (glossary / "term_registry.json").write_text(json.dumps({"terms": [{
        "id": TERM_ID,
        "zh_cn": ["比赛", "赛事"],
        "target_vi": "Cuộc đua",
        "locked": True,
    }]}, ensure_ascii=False), encoding="utf-8")
    (glossary / "ui_community_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "canonical_findings.json").write_text(json.dumps({"findings": [{
        "finding_id": FINDING_ID,
        "status": "open",
        "canonical_resolution": None,
        "evidence": [{
            "source_path": "text_data_dict.json",
            "json_path": ["163", "1035"],
            "source_text": "我的梦想是成为德比赛马娘！",
            "current_text": "Ước mơ của tôi là trở thành Uma Musume Derby!",
        }],
    }]}, ensure_ascii=False), encoding="utf-8")

    assert harden(tmp_path) is True
    assert harden(tmp_path) is False
    terms = load_locked_terms(tmp_path)
    assert locked_term_matches("参加比赛", "Tham gia Cuộc đua", terms)
    assert locked_term_matches("德比赛马娘", "Uma Musume Derby", terms) == []
    assert resolve(tmp_path) is True
    payload = json.loads((glossary / "canonical_findings.json").read_text(encoding="utf-8"))
    assert payload["findings"][0]["canonical_resolution"] == {
        "layer": "context_guard", "term_id": TERM_ID, "target_vi": "Cuộc đua"
    }

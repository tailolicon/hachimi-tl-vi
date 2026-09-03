from __future__ import annotations

import json
from pathlib import Path

from scripts.resolve_context_guard_findings import resolve
from scripts.translation_review_common import community_term_matches, load_community_terms

FINDING_ID = "cf-05ee17c3f625371f"
TERM_ID = "race_state.rushed.text131"


def _write(root: Path) -> None:
    glossary = root / "glossary"
    glossary.mkdir(parents=True)
    (glossary / "ui_community_terms.json").write_text(
        json.dumps({
            "terms": [{
                "id": TERM_ID,
                "source_aliases": ["焦躁"],
                "preferred": "Rushed",
                "accepted": ["Rushed"],
                "compact": [],
                "forbidden": ["Nóng vội", "nóng vội", "焦躁"],
                "require_accepted": True,
                "source_paths": ["text_data_dict.json"],
                "json_path_prefixes": [["131"]],
                "match_mode": "contains",
            }]
        }, ensure_ascii=False),
        encoding="utf-8",
    )
    (glossary / "term_registry.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "canonical_findings.json").write_text(
        json.dumps({
            "findings": [{
                "finding_id": FINDING_ID,
                "status": "open",
                "canonical_resolution": None,
                "evidence": [{
                    "source_path": "text_data_dict.json",
                    "json_path": ["128", "1103"],
                    "source_text": "如同阳光一般温暖你的心。不用焦躁，慢慢来──\\n一步一脚印地前进，梦想正在彼方等着我们。",
                    "current_text": "Ấm áp trái tim bạn như ánh mặt trời. Đừng vội, cứ từ từ thôi──\\nTiến từng bước vững chắc, giấc mơ đang chờ chúng ta ở phía trước.",
                }],
            }]
        }, ensure_ascii=False),
        encoding="utf-8",
    )


def test_rushed_system_label_does_not_fire_in_category_128_prose(tmp_path: Path) -> None:
    _write(tmp_path)
    terms = load_community_terms(tmp_path)

    prose = community_term_matches(
        None,
        "不用焦躁，慢慢来",
        "Đừng vội, cứ từ từ thôi",
        terms,
        source_path="text_data_dict.json",
        json_path=["128", "1103"],
    )
    assert not any(match["id"] == TERM_ID for match in prose)

    race_state = community_term_matches(
        None,
        "保持冷静，避免焦躁",
        "Giữ bình tĩnh, tránh Rushed",
        terms,
        source_path="text_data_dict.json",
        json_path=["131", "9001"],
    )
    assert any(match["id"] == TERM_ID for match in race_state)

    assert resolve(tmp_path) is True
    payload = json.loads((tmp_path / "glossary" / "canonical_findings.json").read_text(encoding="utf-8"))
    assert payload["findings"][0]["canonical_resolution"] == {
        "layer": "context_guard",
        "term_id": TERM_ID,
        "target_vi": "Rushed",
    }

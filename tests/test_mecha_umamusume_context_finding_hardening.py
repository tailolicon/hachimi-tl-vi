from __future__ import annotations

import json
from pathlib import Path

from scripts.harden_mecha_umamusume_context_finding import TERM_ID, harden
from scripts.resolve_context_guard_findings import resolve
from scripts.translation_review_common import community_term_matches, load_community_terms

FINDING_ID = "cf-9844f9093f379eac"


def test_mecha_proper_name_excludes_generic_umamusume_and_resolves(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir(parents=True)
    (glossary / "ui_community_terms.json").write_text(json.dumps({"terms": [{
        "id": TERM_ID,
        "source_aliases": ["赛马娘"],
        "preferred": "Mã Nương",
        "accepted": ["Mã Nương"],
        "forbidden": ["Uma Musume"],
        "require_accepted": True,
    }]}, ensure_ascii=False), encoding="utf-8")
    (glossary / "term_registry.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "canonical_findings.json").write_text(json.dumps({"findings": [{
        "finding_id": FINDING_ID,
        "status": "open",
        "canonical_resolution": None,
        "evidence": [{
            "source_path": "text_data_dict.json",
            "json_path": ["14", "200803"],
            "source_text": "决胜服（机械赛马娘第三阶段）",
            "current_text": "Trang phục chiến thắng (Mecha Uma Musume giai đoạn 3)",
        }],
    }]}, ensure_ascii=False), encoding="utf-8")

    assert harden(tmp_path) is True
    assert harden(tmp_path) is False
    terms = load_community_terms(tmp_path)
    assert community_term_matches(None, "普通赛马娘", "Mã Nương bình thường", terms)

    mecha_proper = community_term_matches(
        None,
        "决胜服（机械赛马娘第三阶段）",
        "Trang phục chiến thắng (Mecha Uma Musume giai đoạn 3)",
        terms,
        source_path="text_data_dict.json",
        json_path=["14", "200803"],
    )
    assert not any(row["id"] == TERM_ID for row in mecha_proper)

    generic_mecha_description = community_term_matches(
        None,
        "机械赛马娘详情",
        "Chi tiết Mã Nương Mecha",
        terms,
        source_path="text_data_dict.json",
        json_path=["14", "999999"],
    )
    assert any(row["id"] == TERM_ID for row in generic_mecha_description)

    assert resolve(tmp_path) is True
    payload = json.loads((glossary / "canonical_findings.json").read_text(encoding="utf-8"))
    assert payload["findings"][0]["canonical_resolution"] == {
        "layer": "context_guard", "term_id": TERM_ID, "target_vi": "Mã Nương"
    }

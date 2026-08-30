from __future__ import annotations

import json
from pathlib import Path

from scripts.resolve_context_guard_findings import resolve


def test_fast_step_context_finding_resolves_with_exact_skill_guard(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir(parents=True)
    (glossary / "ui_community_terms.json").write_text('{"terms": []}\n', encoding="utf-8")
    (glossary / "term_registry.json").write_text(json.dumps({"terms": [{
        "id": "reviewed.skill_name.e778cffef185",
        "zh_cn": ["快人一步"],
        "target_vi": "Một bước vượt lên",
        "locked": True,
        "match_mode": "exact",
    }]}, ensure_ascii=False), encoding="utf-8")
    (glossary / "canonical_findings.json").write_text(json.dumps({"findings": [{
        "finding_id": "cf-b4ddf0728febc08f",
        "status": "open",
        "source_zh_cn": "快人一步",
        "canonical_resolution": None,
        "evidence": [{
            "source_path": "text_data_dict.json",
            "json_path": ["143", "7"],
            "source_text": "融会贯通的速度快人一步！",
            "current_text": "Nhờ tinh thông mọi thứ, tốc độ luôn đi trước một bước!",
        }],
    }]}, ensure_ascii=False), encoding="utf-8")
    assert resolve(tmp_path) is True
    payload = json.loads((glossary / "canonical_findings.json").read_text(encoding="utf-8"))
    assert payload["findings"][0]["canonical_resolution"]["term_id"] == "reviewed.skill_name.e778cffef185"

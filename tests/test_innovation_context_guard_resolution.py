from __future__ import annotations

import json
from pathlib import Path

from scripts.resolve_context_guard_findings import resolve


def test_innovation_context_finding_resolves_with_exact_skill_guard(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir(parents=True)
    (glossary / "ui_community_terms.json").write_text('{"terms": []}\n', encoding="utf-8")
    (glossary / "term_registry.json").write_text(json.dumps({"terms": [{
        "id": "reviewed.skill_name.5dffb471df59",
        "zh_cn": ["革新"],
        "target_vi": "Đổi mới",
        "locked": True,
        "match_mode": "exact",
    }]}, ensure_ascii=False), encoding="utf-8")
    (glossary / "canonical_findings.json").write_text(json.dumps({"findings": [{
        "finding_id": "cf-4247246a96780f8b",
        "status": "open",
        "source_zh_cn": "革新",
        "canonical_resolution": None,
        "evidence": [{
            "source_path": "text_data_dict.json",
            "json_path": ["163", "1138"],
            "source_text": "掀起一场革新，不是吗！",
            "current_text": "Phải tạo nên một cuộc cách mạng chứ!",
        }],
    }]}, ensure_ascii=False), encoding="utf-8")
    assert resolve(tmp_path) is True
    payload = json.loads((glossary / "canonical_findings.json").read_text(encoding="utf-8"))
    assert payload["findings"][0]["canonical_resolution"]["term_id"] == "reviewed.skill_name.5dffb471df59"

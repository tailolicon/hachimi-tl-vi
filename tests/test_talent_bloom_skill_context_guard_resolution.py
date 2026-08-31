from __future__ import annotations

import json
from pathlib import Path

from scripts.resolve_context_guard_findings import resolve


def test_talent_bloom_finding_resolves_after_exact_guard(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir(parents=True)
    (glossary / "ui_community_terms.json").write_text('{"terms": []}\n', encoding="utf-8")
    registry = {"terms": [{
        "id": "reviewed.skill_name.0be1f248cf96",
        "zh_cn": ["开花"],
        "target_vi": "Nở rộ",
        "locked": True,
        "match_mode": "exact",
        "invalidation_scope": "item",
    }]}
    (glossary / "term_registry.json").write_text(json.dumps(registry, ensure_ascii=False), encoding="utf-8")
    ledger = {"findings": [{
        "finding_id": "cf-0477e3b1d68a9798",
        "status": "open",
        "source_zh_cn": "才能开花",
        "canonical_resolution": None,
        "evidence": [{
            "source_path": "text_data_dict.json",
            "json_path": ["114", "114501"],
            "source_text": "用于解锁育成赛马娘或才能开花。",
            "current_text": "Dùng để mở khóa Mã Nương huấn luyện hoặc Nở rộ tài năng.",
        }],
    }]}
    (glossary / "canonical_findings.json").write_text(json.dumps(ledger, ensure_ascii=False), encoding="utf-8")
    assert resolve(tmp_path) is True
    payload = json.loads((glossary / "canonical_findings.json").read_text(encoding="utf-8"))
    assert payload["findings"][0]["canonical_resolution"] == {
        "layer": "context_guard",
        "term_id": "reviewed.skill_name.0be1f248cf96",
        "target_vi": "Nở rộ",
    }

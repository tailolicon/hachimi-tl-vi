from __future__ import annotations

import json
from pathlib import Path

from scripts.resolve_context_guard_findings import resolve


def test_recovery_spirit_context_finding_resolves_after_scope_guard(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir(parents=True)
    (glossary / "ui_community_terms.json").write_text('{"terms": []}\n', encoding="utf-8")
    registry = {"terms": [{
        "id": "reviewed.condition.97c2a1f26a21",
        "zh_cn": ["恢复精神"],
        "target_vi": "Recovery Spirit",
        "locked": True,
        "match_mode": "exact",
        "source_paths": ["text_data_dict.json"],
        "json_path_prefixes": [["142"]],
    }]}
    (glossary / "term_registry.json").write_text(json.dumps(registry, ensure_ascii=False), encoding="utf-8")
    ledger = {"findings": [{
        "finding_id": "cf-97e98b6571188de5",
        "status": "open",
        "source_zh_cn": "恢复精神",
        "canonical_resolution": None,
        "evidence": [{
            "source_path": "text_data_dict.json",
            "json_path": ["10", "32"],
            "source_text": "喝了恢复精神吧！\n使用后TP恢复30。",
            "current_text": "Uống để lấy lại tinh thần!\nKhi dùng, hồi 30 TP.",
        }],
    }]}
    (glossary / "canonical_findings.json").write_text(json.dumps(ledger, ensure_ascii=False), encoding="utf-8")
    assert resolve(tmp_path) is True
    payload = json.loads((glossary / "canonical_findings.json").read_text(encoding="utf-8"))
    assert payload["findings"][0]["canonical_resolution"] == {
        "layer": "context_guard",
        "term_id": "reviewed.condition.97c2a1f26a21",
        "target_vi": "Recovery Spirit",
    }

from __future__ import annotations

import json
from pathlib import Path

from scripts.resolve_context_guard_findings import resolve


def test_jewel_overlap_resolves_only_after_locked_term_guard(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir(parents=True)
    (glossary / "ui_community_terms.json").write_text('{"terms": []}\n', encoding="utf-8")
    registry = {
        "terms": [{
            "id": "currency.jewel",
            "zh_cn": ["宝石"],
            "target_vi": "Jewel",
            "locked": True,
        }]
    }
    (glossary / "term_registry.json").write_text(json.dumps(registry, ensure_ascii=False), encoding="utf-8")
    ledger = {
        "findings": [{
            "finding_id": "cf-d1bcaa0ab582cbdf",
            "status": "open",
            "source_zh_cn": "宝石",
            "canonical_resolution": None,
            "evidence": [{
                "source_path": "text_data_dict.json",
                "json_path": ["10", "10148"],
                "source_text": "第一红宝石制作的手工巧克力。",
                "current_text": "Chocolate thủ công do Daiichi Ruby làm.",
            }],
        }]
    }
    (glossary / "canonical_findings.json").write_text(json.dumps(ledger, ensure_ascii=False), encoding="utf-8")
    assert resolve(tmp_path) is False

    registry["terms"][0]["exclude_source_contains"] = ["第一红宝石"]
    (glossary / "term_registry.json").write_text(json.dumps(registry, ensure_ascii=False), encoding="utf-8")
    assert resolve(tmp_path) is True
    payload = json.loads((glossary / "canonical_findings.json").read_text(encoding="utf-8"))
    assert payload["findings"][0]["canonical_resolution"] == {
        "layer": "context_guard",
        "term_id": "currency.jewel",
        "target_vi": "Jewel",
    }

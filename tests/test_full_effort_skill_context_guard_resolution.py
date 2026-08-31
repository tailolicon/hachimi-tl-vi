from __future__ import annotations

import json
from pathlib import Path

from scripts.resolve_context_guard_findings import resolve


def test_full_effort_skill_finding_resolves_after_exact_guard(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir(parents=True)
    (glossary / "ui_community_terms.json").write_text('{"terms": []}\n', encoding="utf-8")
    registry = {"terms": [{
        "id": "reviewed.skill_name.5907479481a9",
        "zh_cn": ["全力"],
        "target_vi": "Dốc hết sức",
        "locked": True,
        "match_mode": "exact",
        "invalidation_scope": "item",
    }]}
    (glossary / "term_registry.json").write_text(json.dumps(registry, ensure_ascii=False), encoding="utf-8")
    ledger = {"findings": [{
        "finding_id": "cf-04aeb4f2712eb3c6",
        "status": "open",
        "source_zh_cn": "全力",
        "canonical_resolution": None,
        "evidence": [{
            "source_path": "localize_dict.json",
            "json_path": ["SingleModeScenarioCook425083"],
            "source_text": "尽全力打理了农田！\n<color=#FF6D26>{0}</color>似乎尤其会顺利成长",
            "current_text": "Đã dốc toàn lực chăm sóc nông trại!\n<color=#FF6D26>{0}</color> có vẻ sẽ phát triển đặc biệt thuận lợi",
        }],
    }]}
    (glossary / "canonical_findings.json").write_text(json.dumps(ledger, ensure_ascii=False), encoding="utf-8")
    assert resolve(tmp_path) is True
    payload = json.loads((glossary / "canonical_findings.json").read_text(encoding="utf-8"))
    assert payload["findings"][0]["canonical_resolution"] == {
        "layer": "context_guard",
        "term_id": "reviewed.skill_name.5907479481a9",
        "target_vi": "Dốc hết sức",
    }

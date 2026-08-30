from __future__ import annotations

import json
from pathlib import Path

from scripts.resolve_context_guard_findings import resolve


def _write(root: Path, *, exclusions: list[str]) -> None:
    glossary = root / "glossary"
    glossary.mkdir(parents=True)
    (glossary / "ui_community_terms.json").write_text(
        json.dumps({
            "terms": [{
                "id": "common.stat.power",
                "source_aliases": ["力量"],
                "preferred": "Power",
                "accepted": ["Power"],
                "forbidden": ["Sức mạnh"],
                "require_accepted": True,
                "exclude_source_contains": exclusions,
            }]
        }, ensure_ascii=False),
        encoding="utf-8",
    )
    (glossary / "canonical_findings.json").write_text(
        json.dumps({
            "schema_version": 1,
            "findings": [{
                "finding_id": "cf-5d23e532c5359881",
                "status": "open",
                "source_zh_cn": "力量",
                "kinds": ["context_rule"],
                "canonical_resolution": None,
                "evidence": [{
                    "source_path": "text_data_dict.json",
                    "json_path": ["130", "181"],
                    "source_text": "商品的力量",
                    "current_text": "Sức mạnh của hàng hóa",
                }],
            }],
        }, ensure_ascii=False),
        encoding="utf-8",
    )


def test_resolves_only_after_evidence_is_guarded(tmp_path: Path) -> None:
    _write(tmp_path, exclusions=[])
    assert resolve(tmp_path) is False
    payload = json.loads((tmp_path / "glossary" / "canonical_findings.json").read_text(encoding="utf-8"))
    assert payload["findings"][0]["canonical_resolution"] is None

    terms = json.loads((tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8"))
    terms["terms"][0]["exclude_source_contains"] = ["商品的力量"]
    (tmp_path / "glossary" / "ui_community_terms.json").write_text(json.dumps(terms, ensure_ascii=False), encoding="utf-8")
    assert resolve(tmp_path) is True
    assert resolve(tmp_path) is False
    payload = json.loads((tmp_path / "glossary" / "canonical_findings.json").read_text(encoding="utf-8"))
    assert payload["findings"][0]["canonical_resolution"] == {
        "layer": "context_guard",
        "term_id": "common.stat.power",
        "target_vi": "Power",
    }

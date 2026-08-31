from __future__ import annotations

import json
from pathlib import Path

from scripts.resolve_context_guard_findings import resolve
from scripts.translation_review_common import community_term_matches, load_community_terms


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


def test_narrative_guard_preserves_real_power_stat_context(tmp_path: Path) -> None:
    _write(tmp_path, exclusions=["商品的力量"])
    terms = load_community_terms(tmp_path)

    narrative = community_term_matches(
        None,
        "商品的力量",
        "Sức mạnh của hàng hóa",
        terms,
        source_path="text_data_dict.json",
        json_path=["130", "181"],
    )
    assert not any(match["id"] == "common.stat.power" for match in narrative)

    stat_cap = community_term_matches(
        None,
        "力量上限和智力上限提升",
        "Giới hạn Power và Wit tăng",
        terms,
        source_path="text_data_dict.json",
        json_path=["172", "10980101"],
    )
    power = next(match for match in stat_cap if match["id"] == "common.stat.power")
    assert power["accepted_present"] is True
    assert power["forbidden_present"] is False


def test_context_guard_does_not_overwrite_positive_canonical_resolution(tmp_path: Path) -> None:
    _write(tmp_path, exclusions=["商品的力量"])
    payload = json.loads((tmp_path / "glossary" / "canonical_findings.json").read_text(encoding="utf-8"))
    payload["findings"][0]["canonical_resolution"] = {
        "layer": "community",
        "term_id": "system.example.positive",
        "target_vi": "Positive System Label",
    }
    (tmp_path / "glossary" / "canonical_findings.json").write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    assert resolve(tmp_path) is False
    resolved = json.loads((tmp_path / "glossary" / "canonical_findings.json").read_text(encoding="utf-8"))
    assert resolved["findings"][0]["canonical_resolution"] == {
        "layer": "community",
        "term_id": "system.example.positive",
        "target_vi": "Positive System Label",
    }

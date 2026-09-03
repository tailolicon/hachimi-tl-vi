from __future__ import annotations

import json
from pathlib import Path

from scripts.harden_running_style_narrative_finding import NARRATIVE_EXCLUSIONS, harden
from scripts.resolve_running_style_narrative_finding import FINDING_ID, resolve
from scripts.translation_review_common import community_term_matches, load_community_terms


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _seed_terms(root: Path) -> None:
    _write(
        root / "glossary" / "ui_community_terms.json",
        {
            "schema_version": 1,
            "terms": [
                {
                    "id": "common.style",
                    "category": "mechanic",
                    "source_aliases": ["跑法"],
                    "preferred": "Style",
                    "compact": [],
                    "accepted": ["Style"],
                    "forbidden": ["Lối chạy"],
                    "require_accepted": True,
                    "invalidation_scope": "item",
                    "match_mode": "contains",
                    "basis": "Common EN-version category label.",
                }
            ],
        },
    )
    _write(root / "glossary" / "terminology_reviews.json", {"schema_version": 1, "decisions": []})


def test_hardener_preserves_ui_style_but_excludes_proven_narrative(tmp_path: Path) -> None:
    _seed_terms(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False
    terms = load_community_terms(tmp_path)

    ui_matches = community_term_matches(
        None, "跑法", "Style", terms, source_path="text_data_dict.json", json_path=["999", "1"]
    )
    assert any(match.get("id") == "common.style" for match in ui_matches)

    for index, source in enumerate(NARRATIVE_EXCLUSIONS):
        matches = community_term_matches(
            None,
            source,
            "cách chạy",
            terms,
            source_path="text_data_dict.json",
            json_path=["163", str(1004 + index)],
        )
        assert all(match.get("id") != "common.style" for match in matches)


def test_resolver_closes_only_neutralized_category_163_evidence(tmp_path: Path) -> None:
    _seed_terms(tmp_path)
    harden(tmp_path)
    evidence = [
        {
            "source_path": "text_data_dict.json",
            "json_path": ["163", key],
            "source_text": source,
            "current_text": "cách chạy",
        }
        for key, source in zip(("1004", "1040", "1054"), NARRATIVE_EXCLUSIONS, strict=True)
    ]
    _write(
        tmp_path / "glossary" / "canonical_findings.json",
        {
            "schema_version": 1,
            "findings": [
                {
                    "finding_id": FINDING_ID,
                    "status": "open",
                    "source_zh_cn": "跑法",
                    "match_mode": "contains",
                    "evidence": evidence,
                    "canonical_resolution": None,
                }
            ],
        },
    )

    assert resolve(tmp_path) is True
    finding = json.loads((tmp_path / "glossary" / "canonical_findings.json").read_text(encoding="utf-8"))["findings"][0]
    assert finding["canonical_resolution"] == {
        "layer": "context_guard",
        "term_id": "common.style",
        "target_vi": "Style",
    }
    assert resolve(tmp_path) is False

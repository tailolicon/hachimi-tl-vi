from __future__ import annotations

import json
from pathlib import Path

from scripts.resolve_context_guard_findings import resolve


def _write(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _seed(tmp_path: Path, *, excluded: bool) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    term = {
        "id": "skill.righteous_path",
        "kind": "skill_name",
        "locked": True,
        "zh_cn": ["正道"],
        "target_vi": "Chính đạo",
        "source_paths": ["text_data_dict.json"],
        "match_mode": "contains",
    }
    if excluded:
        term["exclude_source_contains"] = ["永井正道"]
    _write(glossary / "term_registry.json", {"terms": [term]})
    _write(glossary / "ui_community_terms.json", {"schema_version": 1, "terms": []})
    _write(
        glossary / "canonical_findings.json",
        {
            "schema_version": 1,
            "findings": [
                {
                    "finding_id": "cf-1bd479584e40d767",
                    "status": "open",
                    "source_zh_cn": "永井正道",
                    "match_mode": "contains",
                    "source_paths": ["text_data_dict.json"],
                    "key_exact": [],
                    "json_path_prefixes": [],
                    "suggested_targets_vi": [],
                    "canonical_resolution": None,
                    "review_resolution": None,
                    "evidence": [
                        {
                            "source_path": "text_data_dict.json",
                            "json_path": ["17", "1007"],
                            "source_text": "作曲：永井正道",
                            "current_text": "Sáng tác: Masamichi Nagai",
                        }
                    ],
                }
            ],
        },
    )


def test_resolves_when_righteous_path_alias_is_excluded_from_creator_name(tmp_path: Path) -> None:
    _seed(tmp_path, excluded=True)
    assert resolve(tmp_path) is True
    finding = json.loads((tmp_path / "glossary" / "canonical_findings.json").read_text(encoding="utf-8"))["findings"][0]
    assert finding["canonical_resolution"] == {
        "layer": "context_guard",
        "term_id": "skill.righteous_path",
        "target_vi": "Chính đạo",
    }


def test_stays_open_while_righteous_path_still_overmatches_creator_name(tmp_path: Path) -> None:
    _seed(tmp_path, excluded=False)
    assert resolve(tmp_path) is False
    finding = json.loads((tmp_path / "glossary" / "canonical_findings.json").read_text(encoding="utf-8"))["findings"][0]
    assert finding["canonical_resolution"] is None

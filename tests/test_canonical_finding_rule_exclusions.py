from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import refresh_canonical_resolutions


def _seed(root: Path) -> None:
    glossary = root / "glossary"
    glossary.mkdir(parents=True)
    (glossary / "terminology_reviews.json").write_text("{}", encoding="utf-8")
    (glossary / "ui_community_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "source_bridge_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "skill_name_style.json").write_text(json.dumps({"canonical_examples": []}), encoding="utf-8")
    (glossary / "term_registry.json").write_text(
        json.dumps(
            {
                "terms": [
                    {
                        "id": "skill.righteous_path",
                        "zh_cn": ["正道"],
                        "target_vi": "Chính đạo",
                        "locked": True,
                        "match_mode": "contains",
                        "exclude_source_contains": ["永井正道"],
                    }
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def _finding(source: str) -> dict[str, object]:
    return {
        "finding_id": "cf-test",
        "status": "open",
        "source_zh_cn": source,
        "match_mode": "contains",
        "source_paths": [],
        "key_exact": [],
        "json_path_prefixes": [],
        "suggested_targets_vi": ["Chính đạo"],
        "canonical_resolution": None,
        "review_resolution": None,
    }


def test_excluded_source_does_not_receive_canonical_resolution(tmp_path: Path) -> None:
    _seed(tmp_path)
    ledger = refresh_canonical_resolutions(tmp_path, {"schema_version": 1, "findings": [_finding("作词：永井正道")]})
    assert ledger["findings"][0]["canonical_resolution"] is None


def test_non_excluded_alias_still_receives_canonical_resolution(tmp_path: Path) -> None:
    _seed(tmp_path)
    ledger = refresh_canonical_resolutions(tmp_path, {"schema_version": 1, "findings": [_finding("正道")]})
    assert ledger["findings"][0]["canonical_resolution"] == {
        "layer": "locked",
        "term_id": "skill.righteous_path",
        "target_vi": "Chính đạo",
    }

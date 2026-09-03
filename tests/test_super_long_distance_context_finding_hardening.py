from __future__ import annotations

import json
from pathlib import Path

from scripts.harden_super_long_distance_context_finding import TERM_ID, harden
from scripts.resolve_context_guard_findings import resolve
from scripts.translation_review_common import community_term_matches, load_community_terms

LEGACY_FINDING_ID = "cf-1db30364f26517a5"
CURRENT_FINDING_ID = "cf-072fd00f345e81cb"


def _seed(root: Path, finding_id: str = CURRENT_FINDING_ID) -> None:
    glossary = root / "glossary"
    glossary.mkdir(parents=True)
    (glossary / "ui_community_terms.json").write_text(
        json.dumps({"terms": [{
            "id": TERM_ID,
            "category": "distance",
            "source_aliases": ["長距離", "长距离"],
            "preferred": "Long",
            "accepted": ["Long"],
            "forbidden": ["Cự ly dài"],
            "require_accepted": True,
        }]}, ensure_ascii=False),
        encoding="utf-8",
    )
    (glossary / "canonical_findings.json").write_text(
        json.dumps({
            "schema_version": 1,
            "findings": [{
                "finding_id": finding_id,
                "status": "open",
                "source_zh_cn": "超长距离" if finding_id == CURRENT_FINDING_ID else "长距离",
                "kinds": ["context_rule"],
                "canonical_resolution": None,
                "evidence": [{
                    "source_path": "text_data_dict.json",
                    "json_path": ["147", "2042901"],
                    "source_text": "超长距离恢复○",
                    "current_text": "Hồi phục cự ly siêu dài ○",
                }],
            }],
        }, ensure_ascii=False),
        encoding="utf-8",
    )


def test_super_long_skill_does_not_match_generic_long_and_resolves_finding(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    terms = load_community_terms(tmp_path)
    super_long = community_term_matches(
        None,
        "超长距离恢复○",
        "Hồi phục cự ly siêu dài○",
        terms,
        source_path="text_data_dict.json",
        json_path=["147", "2042901"],
    )
    assert not any(match["id"] == TERM_ID for match in super_long)

    ordinary_long = community_term_matches(
        None,
        "长距离直线○",
        "Long Straight ○",
        terms,
        source_path="text_data_dict.json",
        json_path=["147", "2011101"],
    )
    assert any(match["id"] == TERM_ID for match in ordinary_long)

    assert resolve(tmp_path) is True
    payload = json.loads((tmp_path / "glossary" / "canonical_findings.json").read_text(encoding="utf-8"))
    assert payload["findings"][0]["canonical_resolution"] == {
        "layer": "context_guard",
        "term_id": TERM_ID,
        "target_vi": "Long",
    }


def test_legacy_super_long_finding_id_remains_resolvable(tmp_path: Path) -> None:
    _seed(tmp_path, LEGACY_FINDING_ID)
    assert harden(tmp_path) is True
    assert resolve(tmp_path) is True
    payload = json.loads((tmp_path / "glossary" / "canonical_findings.json").read_text(encoding="utf-8"))
    assert payload["findings"][0]["canonical_resolution"]["term_id"] == TERM_ID

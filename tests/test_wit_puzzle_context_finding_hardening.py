from __future__ import annotations

import json
from pathlib import Path

from scripts.harden_wit_puzzle_context_finding import TERM_ID, harden
from scripts.resolve_context_guard_findings import resolve
from scripts.translation_review_common import community_term_matches, load_community_terms

LEGACY_FINDING_ID = "cf-fbbcf5f4a79f6cf8"
CURRENT_FINDING_ID = "cf-9758a6327ee17eae"


def _seed(root: Path, finding_id: str = CURRENT_FINDING_ID) -> None:
    glossary = root / "glossary"
    glossary.mkdir(parents=True)
    (glossary / "ui_community_terms.json").write_text(json.dumps({"terms": [{
        "id": TERM_ID,
        "source_aliases": ["賢さ", "智力"],
        "preferred": "Wit",
        "accepted": ["Wit"],
        "forbidden": ["Trí tuệ"],
        "require_accepted": True,
    }]}, ensure_ascii=False), encoding="utf-8")
    (glossary / "canonical_findings.json").write_text(json.dumps({
        "schema_version": 1,
        "findings": [{
            "finding_id": finding_id,
            "status": "open",
            "source_zh_cn": "智力扣" if finding_id == CURRENT_FINDING_ID else "智力",
            "kinds": ["context_rule"],
            "canonical_resolution": None,
            "evidence": [{
                "source_path": "text_data_dict.json",
                "json_path": ["165", "1143"],
                "source_text": "解智力扣",
                "current_text": "Giải vòng khóa trí tuệ",
            }],
        }],
    }, ensure_ascii=False), encoding="utf-8")


def test_wit_alias_does_not_match_puzzle_and_context_finding_resolves(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False
    terms = load_community_terms(tmp_path)

    puzzle = community_term_matches(None, "解智力扣", "Giải vòng khóa trí tuệ", terms, source_path="text_data_dict.json", json_path=["165", "1143"])
    assert not any(match["id"] == TERM_ID for match in puzzle)

    stat = community_term_matches(None, "智力上限提升", "Giới hạn Wit tăng", terms, source_path="text_data_dict.json", json_path=["172", "1"])
    assert any(match["id"] == TERM_ID for match in stat)

    assert resolve(tmp_path) is True
    payload = json.loads((tmp_path / "glossary" / "canonical_findings.json").read_text(encoding="utf-8"))
    assert payload["findings"][0]["canonical_resolution"] == {
        "layer": "context_guard",
        "term_id": TERM_ID,
        "target_vi": "Wit",
    }


def test_legacy_wit_puzzle_finding_id_remains_resolvable(tmp_path: Path) -> None:
    _seed(tmp_path, LEGACY_FINDING_ID)
    assert harden(tmp_path) is True
    assert resolve(tmp_path) is True
    payload = json.loads((tmp_path / "glossary" / "canonical_findings.json").read_text(encoding="utf-8"))
    assert payload["findings"][0]["canonical_resolution"]["term_id"] == TERM_ID

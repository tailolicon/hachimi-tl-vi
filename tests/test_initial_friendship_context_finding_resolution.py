from __future__ import annotations

import json
from pathlib import Path

from scripts.resolve_context_guard_findings import resolve


FINDING_ID = "cf-375c57aaf697bbff"
TERM_ID = "support.initial_friendship.effect155"


def _write(root: Path, *, evidence_path: list[str]) -> None:
    glossary = root / "glossary"
    glossary.mkdir(parents=True)
    (glossary / "term_registry.json").write_text(
        json.dumps({"terms": []}, ensure_ascii=False), encoding="utf-8"
    )
    (glossary / "ui_community_terms.json").write_text(
        json.dumps(
            {
                "terms": [
                    {
                        "id": TERM_ID,
                        "source_aliases": ["初始牵绊值", "初始羁绊值", "初始羁绊槽上升"],
                        "preferred": "Initial Friendship",
                        "accepted": ["Initial Friendship"],
                        "compact": [],
                        "forbidden": ["Liên kết ban đầu"],
                        "require_accepted": True,
                        "source_paths": ["text_data_dict.json"],
                        "json_path_prefixes": [["155"]],
                        "match_mode": "contains",
                        "invalidation_scope": "item",
                    }
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (glossary / "canonical_findings.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "findings": [
                    {
                        "finding_id": FINDING_ID,
                        "status": "open",
                        "source_zh_cn": "初始牵绊值",
                        "match_mode": "contains",
                        "source_paths": ["text_data_dict.json"],
                        "json_path_prefixes": [],
                        "suggested_targets_vi": ["Initial Friendship"],
                        "canonical_resolution": None,
                        "evidence": [
                            {
                                "source_path": "text_data_dict.json",
                                "json_path": evidence_path,
                                "source_text": "友情加成&初始牵绊值提升",
                                "current_text": "Friendship Bonus & Initial Friendship",
                            }
                        ],
                    }
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def test_resolves_source_path_wide_finding_when_all_evidence_is_in_effect155(tmp_path: Path) -> None:
    _write(tmp_path, evidence_path=["155", "20016"])
    assert resolve(tmp_path) is True
    payload = json.loads((tmp_path / "glossary" / "canonical_findings.json").read_text(encoding="utf-8"))
    assert payload["findings"][0]["canonical_resolution"] == {
        "layer": "community",
        "term_id": TERM_ID,
        "target_vi": "Initial Friendship",
    }


def test_does_not_resolve_if_any_evidence_escapes_effect155_scope(tmp_path: Path) -> None:
    _write(tmp_path, evidence_path=["163", "999"])
    assert resolve(tmp_path) is False
    payload = json.loads((tmp_path / "glossary" / "canonical_findings.json").read_text(encoding="utf-8"))
    assert payload["findings"][0]["canonical_resolution"] is None

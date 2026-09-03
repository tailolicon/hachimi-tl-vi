from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import active_findings, refresh_canonical_resolutions
from scripts.harden_uma_musume_stakes_component_finding import (
    DECISION,
    FINDING_ID,
    PREFERRED,
    SOURCE_JA,
    SOURCE_ZH,
    TERM_ID,
    WORLD_TERM_ID,
    harden,
)


def _seed(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    (glossary / "ui_community_terms.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "terms": [
                    {
                        "id": WORLD_TERM_ID,
                        "category": "world",
                        "source_aliases": ["赛马娘"],
                        "preferred": "Mã Nương",
                        "accepted": ["Mã Nương"],
                        "forbidden": ["Uma Musume"],
                        "require_accepted": True,
                        "match_mode": "contains",
                    },
                    {
                        "id": TERM_ID,
                        "category": "race",
                        "source_aliases": [SOURCE_ZH],
                        "preferred": PREFERRED,
                        "accepted": [PREFERRED],
                        "source_paths": ["text_data_dict.json"],
                        "json_path_prefixes": [["131"]],
                        "match_mode": "contains",
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    (glossary / "terminology_reviews.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "decisions": [
                    {
                        "decision_id": DECISION["decision_id"],
                        "source_zh_cn": SOURCE_ZH,
                        "action": "lock",
                        "target_vi": PREFERRED,
                        "source_paths": ["text_data_dict.json"],
                        "json_path_prefixes": [["131"]],
                        "match_mode": "contains",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    (glossary / "term_registry.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "source_bridge_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")


def _finding(*, source_path: str = "text_data_dict.json") -> dict[str, object]:
    return {
        "finding_id": FINDING_ID,
        "status": "open",
        "source_zh_cn": SOURCE_ZH,
        "match_mode": "contains",
        "source_paths": [source_path],
        "key_exact": [],
        "json_path_prefixes": [],
        "suggested_targets_vi": [],
        "canonical_resolution": None,
        "review_resolution": None,
    }


def test_uma_musume_stakes_live_shape_resolves_and_is_idempotent(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    community = json.loads((tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8"))
    world = next(item for item in community["terms"] if item["id"] == WORLD_TERM_ID)
    term = next(item for item in community["terms"] if item["id"] == TERM_ID)
    assert SOURCE_ZH in world["exclude_source_contains"]
    assert term["preferred"] == PREFERRED
    assert term["source_paths"] == ["text_data_dict.json"]
    assert term["json_path_prefixes"] == []
    assert term["match_mode"] == "contains"
    assert term["invalidation_scope"] == "item"

    reviews = json.loads((tmp_path / "glossary" / "terminology_reviews.json").read_text(encoding="utf-8"))
    decision = next(item for item in reviews["decisions"] if item["decision_id"] == DECISION["decision_id"])
    assert decision["target_vi"] == PREFERRED
    assert decision["ja"] == [SOURCE_JA]
    assert decision["json_path_prefixes"] == []

    payload = refresh_canonical_resolutions(
        tmp_path, {"schema_version": 1, "findings": [_finding()]}
    )
    finding = payload["findings"][0]
    assert finding["canonical_resolution"] == {
        "layer": "community",
        "term_id": TERM_ID,
        "target_vi": PREFERRED,
    }
    assert finding["review_resolution"] == {
        "decision_id": DECISION["decision_id"],
        "action": "lock",
        "target_vi": PREFERRED,
    }
    assert active_findings(payload) == []


def test_component_rule_stays_inside_text_data(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True

    wrong_file = refresh_canonical_resolutions(
        tmp_path,
        {"schema_version": 1, "findings": [_finding(source_path="localize_dict.json")]},
    )["findings"][0]
    assert wrong_file["canonical_resolution"] is None

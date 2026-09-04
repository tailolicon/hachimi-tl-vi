from __future__ import annotations

import json
from pathlib import Path

from scripts.harden_generic_triple_crown_finding import (
    GENERIC_TRIPLE_CROWN,
    GENERIC_TRIPLE_CROWN_DECISION,
    harden,
)


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def test_generic_triple_crown_hardening_is_scoped_and_idempotent(tmp_path: Path) -> None:
    _write(tmp_path / "glossary" / "ui_community_terms.json", {"schema_version": 1, "terms": []})
    _write(tmp_path / "glossary" / "terminology_reviews.json", {"schema_version": 1, "decisions": []})

    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    community = json.loads((tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8"))
    term = next(item for item in community["terms"] if item["id"] == GENERIC_TRIPLE_CROWN["id"])
    assert term["source_aliases"] == ["三冠"]
    assert term["preferred"] == "Triple Crown"
    assert term["accepted"] == ["Triple Crown"]
    assert term["source_paths"] == ["text_data_dict.json"]
    assert term["json_path_prefixes"] == [["144"]]
    assert term["match_mode"] == "contains"
    assert term["invalidation_scope"] == "item"

    reviews = json.loads((tmp_path / "glossary" / "terminology_reviews.json").read_text(encoding="utf-8"))
    decision = next(
        item for item in reviews["decisions"] if item["decision_id"] == GENERIC_TRIPLE_CROWN_DECISION["decision_id"]
    )
    assert decision["source_zh_cn"] == "三冠"
    assert decision["action"] == "lock"
    assert decision["target_vi"] == "Triple Crown"


def test_generic_triple_crown_scope_does_not_claim_compound_crown_categories() -> None:
    term = GENERIC_TRIPLE_CROWN
    assert ["144"] in term["json_path_prefixes"]
    assert ["147"] not in term["json_path_prefixes"]
    assert ["16"] not in term["json_path_prefixes"]
    assert "经典三冠" not in term["source_aliases"]
    assert "春古马三冠" not in term["source_aliases"]
    assert "秋古马三冠" not in term["source_aliases"]

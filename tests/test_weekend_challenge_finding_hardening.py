from __future__ import annotations

import json
from pathlib import Path

from scripts.harden_weekend_challenge_finding import (
    WEEKEND_CHALLENGE,
    WEEKEND_CHALLENGE_DECISION,
    harden,
)


def test_weekend_challenge_hardener_is_scoped_and_idempotent(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    community_path = glossary / "ui_community_terms.json"
    community_path.write_text(
        json.dumps({"schema_version": 1, "terms": []}, ensure_ascii=False),
        encoding="utf-8",
    )
    reviews_path = glossary / "terminology_reviews.json"
    reviews_path.write_text(
        json.dumps({"schema_version": 1, "decisions": []}, ensure_ascii=False),
        encoding="utf-8",
    )

    assert harden(tmp_path) is True
    payload = json.loads(community_path.read_text(encoding="utf-8"))
    term = next(item for item in payload["terms"] if item["id"] == WEEKEND_CHALLENGE["id"])
    assert term["source_aliases"] == ["周末挑战"]
    assert term["preferred"] == "Weekend Challenge"
    assert term["source_paths"] == ["localize_dict.json"]
    assert term["key_exact"] == ["RatingRace600015"]
    assert term["match_mode"] == "contains"
    assert term["invalidation_scope"] == "item"

    reviews = json.loads(reviews_path.read_text(encoding="utf-8"))
    decision = next(
        item for item in reviews["decisions"]
        if item["decision_id"] == WEEKEND_CHALLENGE_DECISION["decision_id"]
    )
    assert decision["source_zh_cn"] == "周末挑战"
    assert decision["action"] == "lock"
    assert decision["target_vi"] == "Weekend Challenge"

    assert harden(tmp_path) is False

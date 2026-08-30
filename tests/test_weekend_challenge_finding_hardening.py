from __future__ import annotations

import json
from pathlib import Path

from scripts.harden_weekend_challenge_finding import WEEKEND_CHALLENGE, harden


def test_weekend_challenge_hardener_is_scoped_and_idempotent(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    path = glossary / "ui_community_terms.json"
    path.write_text(
        json.dumps({"schema_version": 1, "terms": []}, ensure_ascii=False),
        encoding="utf-8",
    )

    assert harden(tmp_path) is True
    payload = json.loads(path.read_text(encoding="utf-8"))
    term = next(item for item in payload["terms"] if item["id"] == WEEKEND_CHALLENGE["id"])
    assert term["source_aliases"] == ["周末挑战"]
    assert term["preferred"] == "Weekend Challenge"
    assert term["source_paths"] == ["localize_dict.json"]
    assert term["key_exact"] == ["RatingRace600015"]
    assert term["match_mode"] == "contains"
    assert term["invalidation_scope"] == "item"

    assert harden(tmp_path) is False

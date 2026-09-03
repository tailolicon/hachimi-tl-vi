from __future__ import annotations

import json
from pathlib import Path

from scripts.harden_heroic_tale_title_finding import (
    HEROIC_TALE_DECISION,
    HEROIC_TALE_TITLE,
    harden,
)


def test_heroic_tale_title_hardener_is_scoped_and_idempotent(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    community_path = glossary / "ui_community_terms.json"
    community_path.write_text(json.dumps({"schema_version": 1, "terms": []}, ensure_ascii=False), encoding="utf-8")
    reviews_path = glossary / "terminology_reviews.json"
    reviews_path.write_text(json.dumps({"schema_version": 1, "decisions": []}, ensure_ascii=False), encoding="utf-8")

    assert harden(tmp_path) is True
    payload = json.loads(community_path.read_text(encoding="utf-8"))
    term = next(item for item in payload["terms"] if item["id"] == HEROIC_TALE_TITLE["id"])
    assert term["source_aliases"] == ["英雄奇谭"]
    assert term["preferred"] == "Anh Hùng Kỳ Đàm"
    assert term["source_paths"] == ["localize_dict.json"]
    assert term["key_prefixes"] == ["Heroes511"]
    assert term["match_mode"] == "contains"
    assert term["invalidation_scope"] == "item"
    assert "Heroic Tale" in term["forbidden"]

    reviews = json.loads(reviews_path.read_text(encoding="utf-8"))
    decision = next(item for item in reviews["decisions"] if item["decision_id"] == HEROIC_TALE_DECISION["decision_id"])
    assert decision["source_zh_cn"] == "英雄奇谭"
    assert decision["action"] == "lock"
    assert decision["target_vi"] == "Anh Hùng Kỳ Đàm"

    assert harden(tmp_path) is False

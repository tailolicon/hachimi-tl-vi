from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import refresh_canonical_resolutions
from scripts.harden_umamusume_idol_source_bridge_finding import RULE, harden
from scripts.translation_review_common import community_term_matches, load_community_terms


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _seed(tmp_path: Path) -> None:
    _write(tmp_path / "glossary" / "ui_community_terms.json", {"schema_version": 1, "terms": []})
    _write(tmp_path / "glossary" / "terminology_reviews.json", {"schema_version": 1, "decisions": []})
    _write(tmp_path / "glossary" / "term_registry.json", {"terms": []})
    _write(tmp_path / "glossary" / "source_bridge_terms.json", {"terms": []})


def test_umamusume_idol_bridge_is_category_scoped_and_idempotent(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    ledger = {"schema_version": 1, "findings": [{
        "finding_id": "cf-de8d8180f7fd53b8",
        "status": "open",
        "source_zh_cn": "马娘偶像",
        "match_mode": "contains",
        "source_paths": ["text_data_dict.json"],
        "key_exact": [],
        "json_path_prefixes": [["128"]],
        "suggested_targets_vi": [],
        "canonical_resolution": None,
        "review_resolution": None,
    }]}
    finding = refresh_canonical_resolutions(tmp_path, ledger)["findings"][0]
    assert finding["canonical_resolution"] == {
        "layer": "community",
        "term_id": RULE["id"],
        "target_vi": "thần tượng Mã Nương",
    }

    terms = load_community_terms(tmp_path)
    matches = community_term_matches(
        None,
        "目标是，顶尖马娘偶像！",
        "Mục tiêu là trở thành thần tượng Mã Nương hàng đầu!",
        terms,
        source_path="text_data_dict.json",
        json_path=["128", "1044"],
    )
    bridge = next(match for match in matches if match["id"] == RULE["id"])
    assert bridge["accepted_present"] is True

    outside = community_term_matches(
        None,
        "马娘偶像",
        "thần tượng Mã Nương",
        terms,
        source_path="text_data_dict.json",
        json_path=["130", "1"],
    )
    assert not any(match["id"] == RULE["id"] for match in outside)

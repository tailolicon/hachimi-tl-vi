from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import active_findings, refresh_canonical_resolutions
from scripts.harden_bucchigiri_road_inheritance_finding import (
    DECISION_ID,
    FINDING_ID,
    INHERITANCE_PREFIXES,
    RULE,
    SOURCE_ZH,
    TARGET,
    TERM_ID,
    harden,
)


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _finding(*, source_path: str = "text_data_dict.json", prefix: str = "172") -> dict:
    return {
        "finding_id": FINDING_ID,
        "status": "open",
        "source_zh_cn": SOURCE_ZH,
        "match_mode": "contains",
        "source_paths": [source_path],
        "key_exact": [],
        "json_path_prefixes": [[prefix]],
        "suggested_targets_vi": [],
        "canonical_resolution": None,
        "review_resolution": None,
    }


def _seed(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    _write(glossary / "ui_community_terms.json", {"schema_version": 1, "terms": []})
    _write(glossary / "terminology_reviews.json", {"schema_version": 1, "decisions": []})
    _write(glossary / "canonical_findings.json", {"schema_version": 1, "findings": [_finding()]})
    _write(glossary / "term_registry.json", {"schema_version": 1, "terms": []})
    _write(glossary / "source_bridge_terms.json", {"schema_version": 1, "terms": []})


def test_hardener_resolves_inheritance_finding_and_is_idempotent(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    community = json.loads((tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8"))
    rule = next(item for item in community["terms"] if item["id"] == TERM_ID)
    assert rule == RULE
    assert rule["json_path_prefixes"] == INHERITANCE_PREFIXES == [["172"]]
    assert rule["match_mode"] == "contains"

    reviews = json.loads((tmp_path / "glossary" / "terminology_reviews.json").read_text(encoding="utf-8"))
    decision = next(item for item in reviews["decisions"] if item["decision_id"] == DECISION_ID)
    assert decision["target_vi"] == TARGET
    assert decision["json_path_prefixes"] == [["172"]]

    ledger = json.loads((tmp_path / "glossary" / "canonical_findings.json").read_text(encoding="utf-8"))
    resolved = refresh_canonical_resolutions(tmp_path, ledger)
    finding = resolved["findings"][0]
    assert finding["canonical_resolution"] == {
        "layer": "community",
        "term_id": TERM_ID,
        "target_vi": TARGET,
    }
    assert finding["review_resolution"] == {
        "decision_id": DECISION_ID,
        "action": "lock",
        "target_vi": TARGET,
    }
    assert active_findings(resolved) == []


def test_inheritance_alias_does_not_escape_category_172_or_text_data(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True

    outside_category = _finding(prefix="128")
    outside_category["suggested_targets_vi"] = [TARGET]
    resolved_category = refresh_canonical_resolutions(
        tmp_path, {"schema_version": 1, "findings": [outside_category]}
    )["findings"][0]
    assert resolved_category["canonical_resolution"] is None

    outside_file = _finding(source_path="localize_dict.json")
    outside_file["suggested_targets_vi"] = [TARGET]
    resolved_file = refresh_canonical_resolutions(
        tmp_path, {"schema_version": 1, "findings": [outside_file]}
    )["findings"][0]
    assert resolved_file["canonical_resolution"] is None

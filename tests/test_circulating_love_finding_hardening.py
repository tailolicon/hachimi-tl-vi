from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import refresh_canonical_resolutions
from scripts.harden_circulating_love_finding import DECISION, FINDING_ID, RULE, TARGET, harden


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _seed(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    _write(glossary / "ui_community_terms.json", {"schema_version": 1, "terms": []})
    _write(glossary / "terminology_reviews.json", {"schema_version": 1, "decisions": []})
    _write(glossary / "term_registry.json", {"terms": []})
    _write(glossary / "source_bridge_terms.json", {"terms": []})
    _write(
        glossary / "canonical_findings.json",
        {
            "schema_version": 1,
            "findings": [
                {
                    "finding_id": FINDING_ID,
                    "status": "open",
                    "source_zh_cn": "爱满人间♡",
                    "match_mode": "contains",
                    "source_paths": ["text_data_dict.json"],
                    "key_exact": [],
                    "json_path_prefixes": [],
                    "suggested_targets_vi": [],
                    "canonical_resolution": None,
                    "review_resolution": None,
                }
            ],
        },
    )


def test_hardener_locks_official_circulating_love_title(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    community = json.loads((tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8"))
    rule = next(item for item in community["terms"] if item["id"] == RULE["id"])
    assert rule["preferred"] == TARGET
    assert rule["match_mode"] == "contains"
    assert "Tình yêu ngập tràn thế gian♡" in rule["forbidden"]

    reviews = json.loads((tmp_path / "glossary" / "terminology_reviews.json").read_text(encoding="utf-8"))
    decision = next(item for item in reviews["decisions"] if item["decision_id"] == DECISION["decision_id"])
    assert decision["target_vi"] == TARGET

    findings = json.loads((tmp_path / "glossary" / "canonical_findings.json").read_text(encoding="utf-8"))
    finding = findings["findings"][0]
    assert TARGET in finding["suggested_targets_vi"]

    refreshed = refresh_canonical_resolutions(tmp_path, findings)["findings"][0]
    assert refreshed["canonical_resolution"] == {
        "layer": "community",
        "term_id": "skill.circulating_love",
        "target_vi": TARGET,
    }


def test_rule_does_not_cover_other_source_file(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    findings = json.loads((tmp_path / "glossary" / "canonical_findings.json").read_text(encoding="utf-8"))
    finding = findings["findings"][0]
    finding["source_paths"] = ["localize_dict.json"]
    refreshed = refresh_canonical_resolutions(tmp_path, findings)["findings"][0]
    assert refreshed["canonical_resolution"] is None

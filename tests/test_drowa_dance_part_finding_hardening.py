import json
from pathlib import Path

from scripts.canonical_findings import active_findings, refresh_canonical_resolutions
from scripts.harden_drowa_dance_part_finding import DECISION, SOURCE, harden


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def test_hardener_is_idempotent_and_ignore_clears_matching_finding(tmp_path: Path) -> None:
    _write(tmp_path / "glossary" / "terminology_reviews.json", {"schema_version": 1, "decisions": []})
    _write(
        tmp_path / "glossary" / "canonical_findings.json",
        {
            "schema_version": 1,
            "findings": [
                {
                    "finding_id": "cf-b74bd0c4b24ab2af",
                    "status": "open",
                    "source_zh_cn": SOURCE,
                    "match_mode": "exact",
                    "source_paths": ["text_data_dict.json"],
                    "key_exact": [],
                    "json_path_prefixes": [["16"]],
                    "canonical_resolution": None,
                    "review_resolution": None,
                }
            ],
        },
    )
    for name in ("term_registry.json", "ui_community_terms.json", "source_bridge_terms.json"):
        _write(tmp_path / "glossary" / name, {"schema_version": 1, "terms": []})
    _write(tmp_path / "glossary" / "skill_name_style.json", {"schema_version": 1, "canonical_examples": []})

    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    reviews = json.loads((tmp_path / "glossary" / "terminology_reviews.json").read_text(encoding="utf-8"))
    decisions = [row for row in reviews["decisions"] if row.get("decision_id") == DECISION["decision_id"]]
    assert decisions == [DECISION]

    refreshed = refresh_canonical_resolutions(tmp_path)
    finding = refreshed["findings"][0]
    assert finding["canonical_resolution"] is None
    assert finding["review_resolution"]["action"] == "ignore"
    assert active_findings(refreshed) == []

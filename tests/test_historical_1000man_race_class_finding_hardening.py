import json
from pathlib import Path

from scripts.canonical_findings import active_findings, refresh_canonical_resolutions
from scripts.harden_historical_1000man_race_class_finding import DECISION_ID, SOURCE, TARGET, TERM_ID, harden
from scripts.translation_review_common import load_community_terms, community_term_matches


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def test_hardener_locks_historical_race_class_and_is_idempotent(tmp_path: Path) -> None:
    _write(tmp_path / "glossary" / "ui_community_terms.json", {"schema_version": 1, "terms": []})
    _write(tmp_path / "glossary" / "terminology_reviews.json", {"schema_version": 1, "decisions": []})
    _write(
        tmp_path / "glossary" / "canonical_findings.json",
        {
            "schema_version": 1,
            "findings": [
                {
                    "finding_id": "cf-6dde20fdd8a4d79c",
                    "status": "open",
                    "source_zh_cn": SOURCE,
                    "match_mode": "exact",
                    "source_paths": ["localize_dict.json"],
                    "key_exact": [],
                    "json_path_prefixes": [],
                    "canonical_resolution": None,
                    "review_resolution": None,
                }
            ],
        },
    )
    for name in ("term_registry.json", "source_bridge_terms.json"):
        _write(tmp_path / "glossary" / name, {"schema_version": 1, "terms": []})
    _write(tmp_path / "glossary" / "skill_name_style.json", {"schema_version": 1, "canonical_examples": []})

    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    terms = json.loads((tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8"))["terms"]
    term = next(row for row in terms if row.get("id") == TERM_ID)
    assert term["preferred"] == TARGET
    assert term["key_exact"] == ["Race0027"]

    matches = community_term_matches(
        "Race0027",
        SOURCE,
        TARGET,
        load_community_terms(tmp_path),
        source_path="localize_dict.json",
        json_path=["Race0027"],
    )
    assert [row["id"] for row in matches] == [TERM_ID]
    assert matches[0]["accepted_present"] is True

    refreshed = refresh_canonical_resolutions(tmp_path)
    finding = refreshed["findings"][0]
    assert finding["canonical_resolution"]["target_vi"] == TARGET
    assert finding["review_resolution"]["decision_id"] == DECISION_ID
    assert active_findings(refreshed) == []

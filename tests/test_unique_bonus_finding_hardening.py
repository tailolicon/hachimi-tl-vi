import json
from pathlib import Path

from scripts.canonical_findings import refresh_canonical_resolutions
from scripts.harden_unique_bonus_finding import ALIAS, DECISION_ID, TARGET, TERM_ID, harden


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _finding(*, match_mode: str = "exact", key_exact: list[str] | None = None, source_path: str = "localize_dict.json", source: str = ALIAS) -> dict:
    return {
        "finding_id": "cf-test-unique-bonus",
        "status": "open",
        "source_zh_cn": source,
        "match_mode": match_mode,
        "source_paths": [source_path],
        "key_exact": key_exact or [],
        "json_path_prefixes": [],
        "kinds": ["system_label"],
        "concepts": ["Character inherent/unique bonus label"],
        "suggested_targets_vi": [],
        "confidence_levels": ["high"],
        "reasons": ["Reusable label needs one canonical player-facing form."],
        "evidence_count": 1,
        "evidence": [],
        "canonical_resolution": None,
        "review_resolution": None,
    }


def _seed(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    _write(glossary / "ui_community_terms.json", {"schema_version": 1, "terms": []})
    _write(glossary / "terminology_reviews.json", {"schema_version": 1, "decisions": []})
    _write(glossary / "term_registry.json", {"schema_version": 1, "terms": []})
    _write(glossary / "source_bridge_terms.json", {"schema_version": 1, "terms": []})


def test_hardener_is_idempotent_and_resolves_exact_and_detail_findings(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    terms = json.loads((tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8"))["terms"]
    term = next(row for row in terms if row["id"] == TERM_ID)
    assert term["preferred"] == TARGET
    assert term["source_paths"] == ["localize_dict.json"]
    assert term["match_mode"] == "contains"
    assert "Unique Bonus" in term["forbidden"]

    for finding in (
        _finding(match_mode="exact"),
        _finding(match_mode="contains", key_exact=["Character0196"]),
    ):
        resolved = refresh_canonical_resolutions(
            tmp_path,
            {"schema_version": 1, "policy": {"canonical": False}, "findings": [finding]},
        )["findings"][0]
        assert resolved["review_resolution"] == {
            "decision_id": DECISION_ID,
            "action": "lock",
            "target_vi": TARGET,
        }
        assert resolved["canonical_resolution"] == {
            "layer": "community",
            "term_id": TERM_ID,
            "target_vi": TARGET,
        }


def test_rule_does_not_resolve_other_source_path_or_other_alias(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    for finding in (
        _finding(source_path="text_data_dict.json"),
        _finding(source="固有技能"),
    ):
        resolved = refresh_canonical_resolutions(
            tmp_path,
            {"schema_version": 1, "policy": {"canonical": False}, "findings": [finding]},
        )["findings"][0]
        assert resolved["canonical_resolution"] is None

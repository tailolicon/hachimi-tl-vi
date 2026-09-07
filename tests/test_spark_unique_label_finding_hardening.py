import json
from pathlib import Path

from scripts.canonical_findings import refresh_canonical_resolutions
from scripts.harden_spark_unique_label_finding import ALIAS, DECISION_ID, TARGET, TERM_ID, harden


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _finding(source_zh_cn: str = ALIAS, source_path: str = "localize_dict.json") -> dict:
    return {
        "finding_id": "cf-55f8aa69cee34bce",
        "status": "open",
        "source_zh_cn": source_zh_cn,
        "match_mode": "exact",
        "source_paths": [source_path],
        "key_exact": [],
        "json_path_prefixes": [],
        "kinds": ["system_label"],
        "concepts": ["Character unique/inherent category label"],
        "suggested_targets_vi": [],
        "confidence_levels": ["high"],
        "reasons": ["Standalone reusable system label requires one canonical player-facing form."],
        "evidence_count": 1,
        "evidence": [],
        "canonical_resolution": None,
        "review_resolution": None,
    }


def _seed(tmp_path: Path) -> Path:
    glossary = tmp_path / "glossary"
    _write(glossary / "ui_community_terms.json", {"schema_version": 1, "terms": []})
    _write(glossary / "terminology_reviews.json", {"schema_version": 1, "decisions": []})
    _write(glossary / "term_registry.json", {"schema_version": 1, "terms": []})
    _write(glossary / "source_bridge_terms.json", {"schema_version": 1, "terms": []})
    return glossary


def test_hardener_is_idempotent_and_resolves_standalone_label(tmp_path: Path) -> None:
    glossary = _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    community = json.loads((glossary / "ui_community_terms.json").read_text(encoding="utf-8"))
    term = next(item for item in community["terms"] if item["id"] == TERM_ID)
    assert term["preferred"] == TARGET
    assert term["source_paths"] == ["localize_dict.json"]
    assert term["match_mode"] == "exact"

    finding = refresh_canonical_resolutions(
        tmp_path,
        {"schema_version": 1, "policy": {"canonical": False}, "findings": [_finding()]},
    )["findings"][0]
    assert finding["review_resolution"] == {
        "decision_id": DECISION_ID,
        "action": "lock",
        "target_vi": TARGET,
    }
    assert finding["canonical_resolution"] == {
        "layer": "community",
        "term_id": TERM_ID,
        "target_vi": TARGET,
    }


def test_other_source_path_and_other_text_are_not_canonicalized(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    for finding in (
        _finding(source_path="text_data_dict.json"),
        _finding(source_zh_cn="固有技能"),
    ):
        resolved = refresh_canonical_resolutions(
            tmp_path,
            {"schema_version": 1, "policy": {"canonical": False}, "findings": [finding]},
        )["findings"][0]
        assert resolved["canonical_resolution"] is None

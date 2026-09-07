import json
from pathlib import Path

from scripts.canonical_findings import active_findings, refresh_canonical_resolutions
from scripts.harden_league_of_heroes_alias_finding import (
    ALIAS,
    BASE_TERM_ID,
    BRIDGE_TERM_ID,
    DECISION_ID,
    FINDING_ID,
    TARGET,
    harden,
)


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _finding(source_path: str = "localize_dict.json") -> dict:
    return {
        "finding_id": FINDING_ID,
        "status": "open",
        "source_zh_cn": ALIAS,
        "match_mode": "contains",
        "source_paths": [source_path],
        "key_exact": [],
        "json_path_prefixes": [],
        "kinds": ["event_name"],
        "concepts": ["League of Heroes event alias"],
        "suggested_targets_vi": [],
        "confidence_levels": ["high"],
        "reasons": ["Named event alias in Heroes UI."],
        "evidence_count": 1,
        "evidence": [],
        "canonical_resolution": None,
        "review_resolution": None,
    }


def _seed(tmp_path: Path, source_path: str = "localize_dict.json") -> Path:
    glossary = tmp_path / "glossary"
    _write(
        glossary / "ui_community_terms.json",
        {
            "schema_version": 1,
            "terms": [
                {
                    "id": BASE_TERM_ID,
                    "category": "event",
                    "source_aliases": ["リーグオブヒーローズ", "英雄联盟赛"],
                    "preferred": TARGET,
                    "compact": ["LoH"],
                    "accepted": [TARGET],
                    "forbidden": ["Liên minh Anh hùng", "Hero League"],
                    "require_accepted": True,
                    "basis": "Canonical League of Heroes event identity.",
                }
            ],
        },
    )
    _write(glossary / "terminology_reviews.json", {"schema_version": 1, "decisions": []})
    _write(glossary / "term_registry.json", {"schema_version": 1, "terms": []})
    _write(glossary / "source_bridge_terms.json", {"schema_version": 1, "terms": []})
    _write(glossary / "canonical_findings.json", {"schema_version": 1, "findings": [_finding(source_path)]})
    return glossary


def test_hardener_bridges_alias_without_broadening_base_rule(tmp_path: Path) -> None:
    glossary = _seed(tmp_path)

    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    community = json.loads((glossary / "ui_community_terms.json").read_text(encoding="utf-8"))
    base = next(item for item in community["terms"] if item["id"] == BASE_TERM_ID)
    bridge = next(item for item in community["terms"] if item["id"] == BRIDGE_TERM_ID)
    assert ALIAS not in base["source_aliases"]
    assert bridge["source_aliases"] == [ALIAS]
    assert bridge["preferred"] == TARGET
    assert bridge["source_paths"] == ["localize_dict.json"]
    assert bridge["match_mode"] == "contains"

    reviews = json.loads((glossary / "terminology_reviews.json").read_text(encoding="utf-8"))
    decision = next(item for item in reviews["decisions"] if item["decision_id"] == DECISION_ID)
    assert decision["action"] == "lock"
    assert decision["target_vi"] == TARGET

    ledger = json.loads((glossary / "canonical_findings.json").read_text(encoding="utf-8"))
    refreshed = refresh_canonical_resolutions(tmp_path, ledger)
    assert active_findings(refreshed) == []
    finding = refreshed["findings"][0]
    assert finding["canonical_resolution"] == {
        "layer": "community",
        "term_id": BRIDGE_TERM_ID,
        "target_vi": TARGET,
    }


def test_bridge_scope_does_not_canonicalize_other_sources(tmp_path: Path) -> None:
    glossary = _seed(tmp_path, "storytimeline.json")

    assert harden(tmp_path) is True
    ledger = json.loads((glossary / "canonical_findings.json").read_text(encoding="utf-8"))
    refreshed = refresh_canonical_resolutions(tmp_path, ledger)
    finding = refreshed["findings"][0]
    assert finding["review_resolution"]["action"] == "lock"
    assert finding["canonical_resolution"] is None

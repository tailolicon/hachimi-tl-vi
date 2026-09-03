import json
from pathlib import Path

from scripts.canonical_findings import refresh_canonical_resolutions
from scripts.harden_loh_main_stage_alias_finding import ALIAS, TERM_ID, harden


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _finding(source_path: str = "localize_dict.json") -> dict:
    return {
        "finding_id": "cf-test-loh-main-stage-alias",
        "status": "open",
        "source_zh_cn": ALIAS,
        "match_mode": "contains",
        "source_paths": [source_path],
        "key_exact": [],
        "json_path_prefixes": [],
        "kinds": ["terminology"],
        "concepts": ["League of Heroes Main Stage alias"],
        "suggested_targets_vi": [],
        "confidence_levels": ["high"],
        "reasons": ["Event-specific Main Stage alias."],
        "evidence_count": 1,
        "evidence": [],
        "canonical_resolution": None,
        "review_resolution": None,
    }


def _community() -> dict:
    return {
        "schema_version": 1,
        "terms": [
            {
                "id": TERM_ID,
                "category": "event",
                "source_aliases": ["メインステージ", "主要阶段"],
                "preferred": "Main Stage",
                "compact": [],
                "accepted": ["Main Stage"],
                "forbidden": ["Giai đoạn chính"],
                "require_accepted": True,
                "basis": "League of Heroes named stage.",
            }
        ],
    }


def test_hardener_extends_existing_main_stage_term_and_resolves_live_scope(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    _write(glossary / "ui_community_terms.json", _community())
    _write(glossary / "term_registry.json", {"schema_version": 1, "terms": []})
    _write(glossary / "source_bridge_terms.json", {"schema_version": 1, "terms": []})

    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    community = json.loads((glossary / "ui_community_terms.json").read_text(encoding="utf-8"))
    term = next(item for item in community["terms"] if item["id"] == TERM_ID)
    assert ALIAS in term["source_aliases"]

    ledger = refresh_canonical_resolutions(
        tmp_path,
        {"schema_version": 1, "policy": {"canonical": False}, "findings": [_finding()]},
    )
    assert ledger["findings"][0]["canonical_resolution"] == {
        "layer": "community",
        "term_id": TERM_ID,
        "target_vi": "Main Stage",
    }


def test_alias_does_not_resolve_outside_localize_source(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    community = _community()
    community["terms"][0]["source_paths"] = ["localize_dict.json"]
    _write(glossary / "ui_community_terms.json", community)
    _write(glossary / "term_registry.json", {"schema_version": 1, "terms": []})
    _write(glossary / "source_bridge_terms.json", {"schema_version": 1, "terms": []})

    assert harden(tmp_path) is True
    ledger = refresh_canonical_resolutions(
        tmp_path,
        {"schema_version": 1, "policy": {"canonical": False}, "findings": [_finding("storytimeline.json")]},
    )
    assert ledger["findings"][0]["canonical_resolution"] is None

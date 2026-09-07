from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import active_findings, refresh_canonical_resolutions
from scripts.harden_gourmet_festival_scenario_finding import FINDING_ID, TARGET, harden


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def test_hardener_covers_source_path_scoped_finding(tmp_path: Path) -> None:
    finding = {
        "finding_id": FINDING_ID,
        "status": "open",
        "source_zh_cn": "大丰食祭",
        "match_mode": "contains",
        "source_paths": ["localize_dict.json"],
        "key_exact": [],
        "json_path_prefixes": [],
        "suggested_targets_vi": [TARGET],
        "canonical_resolution": None,
        "review_resolution": None,
    }
    stale_rule = {
        "id": "scenario.daihoushokusai.short",
        "category": "scenario",
        "source_aliases": ["大丰食祭"],
        "preferred": TARGET,
        "source_paths": ["localize_dict.json"],
        "key_prefixes": ["SingleModeScenarioCook"],
        "match_mode": "contains",
    }
    stale_decision = {
        "decision_id": "audit.finding.scenario-daihoushokusai-short",
        "source_zh_cn": "大丰食祭",
        "action": "lock",
        "target_vi": TARGET,
        "source_paths": ["localize_dict.json"],
        "key_prefixes": ["SingleModeScenarioCook"],
        "match_mode": "contains",
    }
    _write(tmp_path / "glossary/canonical_findings.json", {"schema_version": 1, "findings": [finding]})
    _write(tmp_path / "glossary/terminology_reviews.json", {"schema_version": 1, "decisions": [stale_decision]})
    _write(tmp_path / "glossary/term_registry.json", {"schema_version": 1, "terms": []})
    _write(tmp_path / "glossary/ui_community_terms.json", {"schema_version": 1, "terms": [stale_rule]})
    _write(tmp_path / "glossary/source_bridge_terms.json", {"schema_version": 1, "terms": []})
    _write(tmp_path / "glossary/skill_name_style.json", {"schema_version": 1, "canonical_examples": []})

    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    community = json.loads((tmp_path / "glossary/ui_community_terms.json").read_text(encoding="utf-8"))
    rule = next(row for row in community["terms"] if row["id"] == "scenario.daihoushokusai.short")
    assert "key_prefixes" not in rule
    reviews = json.loads((tmp_path / "glossary/terminology_reviews.json").read_text(encoding="utf-8"))
    decision = next(
        row for row in reviews["decisions"] if row["decision_id"] == "audit.finding.scenario-daihoushokusai-short"
    )
    assert "key_prefixes" not in decision

    ledger = json.loads((tmp_path / "glossary/canonical_findings.json").read_text(encoding="utf-8"))
    refreshed = refresh_canonical_resolutions(tmp_path, ledger)
    assert active_findings(refreshed) == []
    row = refreshed["findings"][0]
    assert row["canonical_resolution"]["target_vi"] == TARGET

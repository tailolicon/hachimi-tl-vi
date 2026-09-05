from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import active_findings, refresh_canonical_resolutions
from scripts.harden_nakayama_uma_musume_stakes_finding import (
    COMMUNITY_RULE,
    DECISION_ID,
    FINDING_ID,
    LEGACY_TERM_ID,
    SOURCE,
    SOURCE_JA,
    TARGET,
    TERM_ID,
    harden,
)


def _seed(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    (glossary / "term_registry.json").write_text(json.dumps({"terms": [{
        "id": LEGACY_TERM_ID, "category": "race_name", "ja": ["中山牝馬ステークス"],
        "zh_cn": [SOURCE], "target_vi": "Nakayama Himba Stakes", "locked": True,
        "source_paths": ["text_data_dict.json"], "json_path_prefixes": [["32"], ["33"], ["111"]],
        "match_mode": "contains", "invalidation_scope": "item",
    }]}), encoding="utf-8")
    (glossary / "ui_community_terms.json").write_text(json.dumps({"schema_version": 1, "terms": [{
        "id": "race.uma_musume_stakes.component131", "category": "race", "source_aliases": ["赛马娘锦标"],
        "preferred": "Uma Musume Stakes", "accepted": ["Uma Musume Stakes"], "require_accepted": True,
        "source_paths": ["text_data_dict.json"], "json_path_prefixes": [], "match_mode": "contains",
    }]}), encoding="utf-8")
    (glossary / "terminology_reviews.json").write_text(json.dumps({"schema_version": 1, "decisions": [{
        "decision_id": "parallel.ctx-old.term-0098.07", "source_zh_cn": SOURCE, "action": "defer"
    }]}), encoding="utf-8")
    (glossary / "source_bridge_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "skill_name_style.json").write_text(json.dumps({"canonical_examples": []}), encoding="utf-8")
    (glossary / "canonical_findings.json").write_text(json.dumps({"schema_version": 1, "findings": [_finding()]}), encoding="utf-8")


def _finding() -> dict[str, object]:
    return {
        "finding_id": FINDING_ID, "status": "open", "source_zh_cn": SOURCE, "match_mode": "exact",
        "source_paths": ["text_data_dict.json"], "key_exact": [], "json_path_prefixes": [],
        "suggested_targets_vi": [], "canonical_resolution": None, "review_resolution": None,
    }


def test_hardener_corrects_game_identity_and_resolves_finding(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False

    registry = json.loads((tmp_path / "glossary/term_registry.json").read_text(encoding="utf-8"))
    race = next(item for item in registry["terms"] if item["id"] == LEGACY_TERM_ID)
    assert race["ja"] == [SOURCE_JA]
    assert race["target_vi"] == TARGET

    community = json.loads((tmp_path / "glossary/ui_community_terms.json").read_text(encoding="utf-8"))
    full = next(item for item in community["terms"] if item["id"] == TERM_ID)
    assert full == COMMUNITY_RULE

    reviews = json.loads((tmp_path / "glossary/terminology_reviews.json").read_text(encoding="utf-8"))
    matching = [item for item in reviews["decisions"] if item.get("source_zh_cn") == SOURCE]
    assert [item["decision_id"] for item in matching] == [DECISION_ID]
    assert matching[0]["action"] == "lock"
    assert matching[0]["target_vi"] == TARGET

    payload = refresh_canonical_resolutions(tmp_path, {"schema_version": 1, "findings": [_finding()]})
    finding = payload["findings"][0]
    assert finding["canonical_resolution"] == {"layer": "community", "term_id": TERM_ID, "target_vi": TARGET}
    assert finding["review_resolution"]["action"] == "lock"
    assert finding["review_resolution"]["target_vi"] == TARGET
    assert active_findings(payload) == []

from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import active_findings, refresh_canonical_resolutions
from scripts.harden_kyoto_himba_precedence_finding import (
    COMPONENT_DECISION_ID,
    COMPONENT_TERM_ID,
    FINDING_ID,
    FULL_TERM_ID,
    SOURCE,
    TARGET,
    harden,
)


def _write(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _seed(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    _write(glossary / "ui_community_terms.json", {"schema_version": 1, "terms": [{"id": COMPONENT_TERM_ID, "category": "race", "source_aliases": ["赛马娘锦标"], "preferred": "Uma Musume Stakes", "accepted": ["Uma Musume Stakes"], "require_accepted": True, "source_paths": ["text_data_dict.json"], "json_path_prefixes": [], "match_mode": "contains"}]})
    _write(glossary / "terminology_reviews.json", {"schema_version": 1, "decisions": [{"decision_id": COMPONENT_DECISION_ID, "source_zh_cn": "赛马娘锦标", "action": "lock", "target_vi": "Uma Musume Stakes", "source_paths": ["text_data_dict.json"], "json_path_prefixes": [], "match_mode": "contains"}]})
    _write(glossary / "term_registry.json", {"terms": [{"id": FULL_TERM_ID, "category": "race", "zh_cn": [SOURCE], "ja": ["京都牝馬ステークス"], "target_vi": TARGET, "locked": True, "source_paths": ["text_data_dict.json"], "json_path_prefixes": [["32"], ["33"], ["111"]], "match_mode": "contains", "invalidation_scope": "item"}]})
    _write(glossary / "source_bridge_terms.json", {"terms": []})
    _write(glossary / "canonical_findings.json", {"schema_version": 1, "findings": [{"finding_id": FINDING_ID, "status": "open", "source_zh_cn": SOURCE, "match_mode": "exact", "source_paths": ["text_data_dict.json"], "key_exact": [], "json_path_prefixes": [["111"]], "suggested_targets_vi": [TARGET], "canonical_resolution": None, "review_resolution": {"decision_id": "legacy.defer", "action": "defer", "target_vi": None}}]})


def test_full_kyoto_race_wins_over_component_and_hardener_is_idempotent(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False
    community = json.loads((tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8"))
    component = next(x for x in community["terms"] if x["id"] == COMPONENT_TERM_ID)
    assert SOURCE in component["exclude_source_exact"]
    payload = json.loads((tmp_path / "glossary" / "canonical_findings.json").read_text(encoding="utf-8"))
    payload = refresh_canonical_resolutions(tmp_path, payload)
    finding = payload["findings"][0]
    assert finding["canonical_resolution"] == {"layer": "locked", "term_id": FULL_TERM_ID, "target_vi": TARGET}
    assert finding["review_resolution"] is None or finding["review_resolution"].get("target_vi") != "Uma Musume Stakes"
    assert active_findings(payload) == []


def test_component_rule_still_covers_plain_component(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    payload = refresh_canonical_resolutions(tmp_path, {"schema_version": 1, "findings": [{"finding_id": "component-positive", "status": "open", "source_zh_cn": "赛马娘锦标", "match_mode": "contains", "source_paths": ["text_data_dict.json"], "key_exact": [], "json_path_prefixes": [], "suggested_targets_vi": [], "canonical_resolution": None, "review_resolution": None}]})
    assert payload["findings"][0]["canonical_resolution"] == {"layer": "community", "term_id": COMPONENT_TERM_ID, "target_vi": "Uma Musume Stakes"}

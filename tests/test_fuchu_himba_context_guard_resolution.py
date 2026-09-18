from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import active_findings, refresh_canonical_resolutions
from scripts.harden_fuchu_himba_context_finding import harden
from scripts.resolve_context_guard_findings import resolve
from scripts.translation_review_common import community_term_matches, load_community_terms

FUCHU_FINDING_ID = "cf-58532e4b9d8093de"
FUCHU_LOCKED_TERM_ID = "reviewed.race_name.bd3f8b5cf8a0"
FUCHU_SOURCE = "府中赛马娘锦标"
FUCHU_TARGET = "Fuchu Uma Musume Stakes"


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _seed(tmp_path: Path) -> None:
    _write(tmp_path / "glossary" / "ui_community_terms.json", {"terms": [{
        "id": "common.world.umamusume",
        "source_aliases": ["赛马娘"],
        "preferred": "Mã Nương",
        "accepted": ["Mã Nương"],
        "forbidden": ["Uma Musume"],
        "require_accepted": True,
    }]})
    _write(tmp_path / "glossary" / "term_registry.json", {"terms": []})
    _write(tmp_path / "glossary" / "canonical_findings.json", {"findings": [{
        "finding_id": "cf-f6302c57277dc9bc",
        "status": "open",
        "source_zh_cn": "赛马娘",
        "match_mode": "contains",
        "source_paths": ["text_data_dict.json"],
        "key_exact": [],
        "json_path_prefixes": [],
        "canonical_resolution": None,
        "review_resolution": None,
        "evidence": [{
            "source_path": "text_data_dict.json",
            "json_path": ["131", "314"],
            "source_text": "取得府中赛马娘锦标（经典级）的胜利",
            "current_text": "Chiến thắng Fuchu Himba Stakes (cấp Classic)",
        }],
    }]})


def test_fuchu_himba_guard_resolves_finding_but_preserves_generic_term(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert resolve(tmp_path) is False
    assert harden(tmp_path) is True
    assert resolve(tmp_path) is True
    assert resolve(tmp_path) is False

    payload = json.loads((tmp_path / "glossary" / "canonical_findings.json").read_text(encoding="utf-8"))
    assert payload["findings"][0]["canonical_resolution"] == {
        "layer": "context_guard",
        "term_id": "common.world.umamusume",
        "target_vi": "Mã Nương",
    }

    terms = load_community_terms(tmp_path)
    race = community_term_matches(
        None,
        "取得府中赛马娘锦标（经典级）的胜利",
        "Chiến thắng Fuchu Himba Stakes (cấp Classic)",
        terms,
        source_path="text_data_dict.json",
        json_path=["131", "314"],
    )
    assert not any(match["id"] == "common.world.umamusume" for match in race)

    generic = community_term_matches(
        None,
        "仅含参加DAY1的★3育成赛马娘！",
        "Chỉ gồm Mã Nương huấn luyện ★3 tham gia DAY1!",
        terms,
        source_path="text_data_dict.json",
        json_path=["13", "50025"],
    )
    uma = next(match for match in generic if match["id"] == "common.world.umamusume")
    assert uma["accepted_present"] is True
    assert uma["forbidden_present"] is False


def _seed_fuchu_full_race_finding(tmp_path: Path, *, category: str = "111") -> dict:
    _seed(tmp_path)
    _write(tmp_path / "glossary" / "term_registry.json", {"terms": [{
        "id": FUCHU_LOCKED_TERM_ID,
        "category": "race_name",
        "zh_cn": [FUCHU_SOURCE],
        "target_vi": FUCHU_TARGET,
        "locked": True,
        "source_paths": ["text_data_dict.json"],
        "json_path_prefixes": [["32"], ["33"], ["111"]],
        "match_mode": "contains",
        "invalidation_scope": "item",
    }]})
    finding = {
        "finding_id": FUCHU_FINDING_ID,
        "status": "open",
        "source_zh_cn": FUCHU_SOURCE,
        "match_mode": "exact",
        "source_paths": ["text_data_dict.json"],
        "key_exact": [],
        "json_path_prefixes": [],
        "suggested_targets_vi": [FUCHU_TARGET],
        "canonical_resolution": {
            "layer": "locked",
            "term_id": FUCHU_LOCKED_TERM_ID,
            "target_vi": FUCHU_TARGET,
        },
        "review_resolution": {
            "decision_id": "audit.finding.fuchu-uma-musume-stakes",
            "action": "lock",
            "target_vi": FUCHU_TARGET,
        },
        "evidence": [{
            "source_path": "text_data_dict.json",
            "json_path": [category, "67"],
            "source_text": FUCHU_SOURCE,
            "current_text": "Fuchu Himba Stakes",
        }],
    }
    return {"schema_version": 1, "findings": [finding]}


def test_source_wide_fuchu_finding_recovers_from_scoped_locked_evidence(tmp_path: Path) -> None:
    payload = _seed_fuchu_full_race_finding(tmp_path)
    refreshed = refresh_canonical_resolutions(tmp_path, payload)
    assert refreshed["findings"][0]["canonical_resolution"] is None

    _write(tmp_path / "glossary" / "canonical_findings.json", refreshed)
    assert resolve(tmp_path) is True
    assert resolve(tmp_path) is False

    resolved = json.loads(
        (tmp_path / "glossary" / "canonical_findings.json").read_text(encoding="utf-8")
    )["findings"][0]
    assert resolved["canonical_resolution"] == {
        "layer": "locked",
        "term_id": FUCHU_LOCKED_TERM_ID,
        "target_vi": FUCHU_TARGET,
    }
    assert active_findings({"findings": [resolved]}) == []


def test_source_wide_fuchu_finding_does_not_resolve_from_out_of_scope_evidence(tmp_path: Path) -> None:
    payload = _seed_fuchu_full_race_finding(tmp_path, category="128")
    refreshed = refresh_canonical_resolutions(tmp_path, payload)
    assert refreshed["findings"][0]["canonical_resolution"] is None
    _write(tmp_path / "glossary" / "canonical_findings.json", refreshed)
    assert resolve(tmp_path) is False
    unresolved = json.loads(
        (tmp_path / "glossary" / "canonical_findings.json").read_text(encoding="utf-8")
    )["findings"][0]
    assert unresolved["canonical_resolution"] is None

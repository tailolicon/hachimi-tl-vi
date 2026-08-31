from __future__ import annotations

import json
from pathlib import Path

from scripts.harden_fuchu_himba_context_finding import harden
from scripts.resolve_context_guard_findings import resolve
from scripts.translation_review_common import community_term_matches, load_community_terms


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

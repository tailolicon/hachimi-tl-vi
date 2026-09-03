from __future__ import annotations

import json
from pathlib import Path

from scripts.harden_aoharu_ignition_finding import AOHARU_IGNITION
from scripts.resolve_regenerated_aoharu_ignition_finding import FINDING_ID, TARGET, TERM_ID, resolve


def _write(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _seed(root: Path, *, include_out_of_scope: bool = False) -> None:
    glossary = root / "glossary"
    glossary.mkdir(parents=True)
    _write(glossary / "ui_community_terms.json", {"schema_version": 1, "terms": [AOHARU_IGNITION]})
    evidence = [{
        "source_path": "text_data_dict.json",
        "json_path": ["147", "2100101"],
        "source_text": "点燃青春・速",
        "current_text": "Thắp lửa thanh xuân・Tốc độ",
    }]
    if include_out_of_scope:
        evidence.append({
            "source_path": "text_data_dict.json",
            "json_path": ["144", "999"],
            "source_text": "点燃青春",
            "current_text": TARGET,
        })
    _write(glossary / "canonical_findings.json", {
        "schema_version": 1,
        "findings": [{
            "finding_id": FINDING_ID,
            "status": "open",
            "source_zh_cn": "点燃青春",
            "match_mode": "contains",
            "source_paths": ["text_data_dict.json"],
            "key_exact": [],
            "json_path_prefixes": [],
            "suggested_targets_vi": [],
            "canonical_resolution": None,
            "review_resolution": None,
            "evidence": evidence,
        }],
    })


def test_regenerated_finding_resolves_when_all_evidence_is_covered(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert resolve(tmp_path) is True
    assert resolve(tmp_path) is False
    payload = json.loads((tmp_path / "glossary" / "canonical_findings.json").read_text(encoding="utf-8"))
    assert payload["findings"][0]["canonical_resolution"] == {
        "layer": "community",
        "term_id": TERM_ID,
        "target_vi": TARGET,
    }


def test_regenerated_finding_stays_open_if_any_evidence_is_outside_scope(tmp_path: Path) -> None:
    _seed(tmp_path, include_out_of_scope=True)
    assert resolve(tmp_path) is False
    payload = json.loads((tmp_path / "glossary" / "canonical_findings.json").read_text(encoding="utf-8"))
    assert payload["findings"][0]["canonical_resolution"] is None

from __future__ import annotations

import json
from pathlib import Path

from scripts.harden_training_support_effect_labels import harden
from scripts.resolve_regenerated_initial_friendship_finding import FINDING_ID, TARGET, TERM_ID, resolve


def _write(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _seed(root: Path, *, covered: bool) -> None:
    _write(root / "glossary/ui_community_terms.json", {"terms": []})
    harden(root)
    current = "Mood Effect & Initial Friendship" if covered else "Mood Effect & Tăng thanh Gắn kết ban đầu"
    _write(root / "glossary/canonical_findings.json", {
        "schema_version": 1,
        "findings": [{
            "finding_id": FINDING_ID,
            "status": "open",
            "source_zh_cn": "初始羁绊槽上升",
            "match_mode": "contains",
            "source_paths": ["text_data_dict.json"],
            "key_exact": [],
            "json_path_prefixes": [],
            "suggested_targets_vi": [TARGET],
            "canonical_resolution": None,
            "review_resolution": None,
            "evidence": [{
                "source_path": "text_data_dict.json",
                "json_path": ["155", "20098"],
                "source_text": "干劲效果提升与初始羁绊槽上升",
                "current_text": current,
            }],
        }],
    })


def test_resolves_only_when_live_evidence_satisfies_scoped_term(tmp_path: Path) -> None:
    _seed(tmp_path, covered=True)
    assert resolve(tmp_path) is True
    assert resolve(tmp_path) is False
    payload = json.loads((tmp_path / "glossary/canonical_findings.json").read_text(encoding="utf-8"))
    assert payload["findings"][0]["canonical_resolution"] == {
        "layer": "community", "term_id": TERM_ID, "target_vi": TARGET
    }


def test_stays_open_when_evidence_still_uses_forbidden_calque(tmp_path: Path) -> None:
    _seed(tmp_path, covered=False)
    assert resolve(tmp_path) is False
    payload = json.loads((tmp_path / "glossary/canonical_findings.json").read_text(encoding="utf-8"))
    assert payload["findings"][0]["canonical_resolution"] is None

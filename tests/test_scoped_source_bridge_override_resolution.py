from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import active_findings
from scripts.resolve_scoped_canonical_overrides import resolve_scoped_canonical_overrides


SOURCE = "神话、哲学、Vu行的发音、业余木工"
TARGET = "Thần thoại, triết học, phát âm các âm V, làm đồ gỗ DIY"
TERM_ID = "source_bridge.tanino_gimlet.v_row_profile"


def _write(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _seed(tmp_path: Path) -> None:
    _write(tmp_path / "glossary" / "ui_community_terms.json", {"terms": []})
    _write(
        tmp_path / "glossary" / "source_bridge_terms.json",
        {
            "terms": [
                {
                    "id": TERM_ID,
                    "zh_cn": [SOURCE],
                    "preferred": TARGET,
                    "accepted": [TARGET],
                    "source_paths": ["text_data_dict.json"],
                    "json_path_prefixes": [["164", "1084"]],
                    "match_mode": "exact",
                }
            ]
        },
    )


def _finding(path: list[str]) -> dict:
    return {
        "finding_id": "cf-46c6157b0331a647",
        "status": "open",
        "source_zh_cn": SOURCE,
        "match_mode": "exact",
        "source_paths": ["text_data_dict.json"],
        "key_exact": [],
        "json_path_prefixes": [],
        "suggested_targets_vi": [],
        "canonical_resolution": None,
        "review_resolution": {
            "decision_id": "audit.finding.tanino-gimlet-v-row-source-bridge",
            "action": "lock",
            "target_vi": TARGET,
        },
        "evidence": [
            {
                "source_path": "text_data_dict.json",
                "json_path": path,
                "source_text": SOURCE,
            }
        ],
    }


def test_scoped_source_bridge_resolves_when_all_evidence_is_covered(tmp_path: Path) -> None:
    _seed(tmp_path)
    ledger = {"schema_version": 1, "findings": [_finding(["164", "1084"])]}
    resolved = resolve_scoped_canonical_overrides(tmp_path, ledger)
    finding = resolved["findings"][0]
    assert finding["canonical_resolution"] == {
        "layer": "source_bridge",
        "term_id": TERM_ID,
        "target_vi": TARGET,
    }
    assert active_findings(resolved) == []


def test_scoped_source_bridge_does_not_cover_evidence_outside_rule(tmp_path: Path) -> None:
    _seed(tmp_path)
    ledger = {"schema_version": 1, "findings": [_finding(["164", "1085"])]}
    resolved = resolve_scoped_canonical_overrides(tmp_path, ledger)
    assert resolved["findings"][0]["canonical_resolution"] is None
    assert len(active_findings(resolved)) == 1

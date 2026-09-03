from __future__ import annotations

import json
from pathlib import Path

from scripts.harden_super_long_distance_context_finding import TERM_ID, harden
from scripts.resolve_regenerated_super_long_distance_context_finding import FINDING_ID, resolve


def _seed(root: Path) -> None:
    glossary = root / "glossary"
    glossary.mkdir(parents=True)
    (glossary / "ui_community_terms.json").write_text(
        json.dumps({"terms": [{
            "id": TERM_ID,
            "category": "distance",
            "source_aliases": ["長距離", "长距离"],
            "preferred": "Long",
            "accepted": ["Long"],
            "forbidden": ["Cự ly dài"],
            "require_accepted": True,
        }]}, ensure_ascii=False),
        encoding="utf-8",
    )
    (glossary / "canonical_findings.json").write_text(
        json.dumps({
            "schema_version": 1,
            "findings": [{
                "finding_id": FINDING_ID,
                "status": "open",
                "source_zh_cn": "超长距离",
                "kinds": ["context_rule"],
                "canonical_resolution": None,
                "evidence": [{
                    "source_path": "text_data_dict.json",
                    "json_path": ["147", "2042901"],
                    "source_text": "超长距离恢复○",
                    "current_text": "Hồi phục cự ly siêu dài ○",
                }],
            }],
        }, ensure_ascii=False),
        encoding="utf-8",
    )


def test_regenerated_finding_resolves_only_after_long_overmatch_is_guarded(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert resolve(tmp_path) is False
    assert harden(tmp_path) is True
    assert resolve(tmp_path) is True
    payload = json.loads((tmp_path / "glossary" / "canonical_findings.json").read_text(encoding="utf-8"))
    assert payload["findings"][0]["canonical_resolution"] == {
        "layer": "context_guard",
        "term_id": TERM_ID,
        "target_vi": "Long",
    }

from __future__ import annotations

import json
from pathlib import Path

from scripts.harden_running_style_sequence_finding import ALIASES, harden
from scripts.resolve_running_style_sequence_finding import EXPECTED_TARGET, FINDING_ID, resolve
from scripts.translation_review_common import community_term_matches, load_community_terms


def _community_terms() -> dict[str, object]:
    return {
        "terms": [
            {"id": "common.style.front_runner", "source_aliases": ["逃げ", "领跑"], "preferred": "Front Runner", "accepted": ["Front Runner"], "forbidden": [], "require_accepted": True},
            {"id": "common.style.late_surger", "source_aliases": ["差し", "差行"], "preferred": "Late Surger", "accepted": ["Late Surger"], "forbidden": [], "require_accepted": True},
            {"id": "common.style.pace_chaser", "source_aliases": ["先行"], "preferred": "Pace Chaser", "accepted": ["Pace Chaser"], "forbidden": [], "require_accepted": True},
            {"id": "common.style.end_closer", "source_aliases": ["追赶"], "preferred": "End Closer", "accepted": ["End Closer"], "forbidden": [], "require_accepted": True},
        ]
    }


def test_running_style_sequence_uses_canonical_en_labels(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir(parents=True)
    (glossary / "ui_community_terms.json").write_text(json.dumps(_community_terms(), ensure_ascii=False), encoding="utf-8")

    assert harden(tmp_path) is True
    assert harden(tmp_path) is False
    terms = load_community_terms(tmp_path)
    source = "使用作战[领放][先行][居中][追赶]分别取得GⅠ级别比赛的胜利"
    target = "Dùng các chiến thuật [Front Runner][Pace Chaser][Late Surger][End Closer] để giành chiến thắng"
    matches = community_term_matches(None, source, target, terms, source_path="text_data_dict.json", json_path=["131", "70"])
    ids = {match["id"] for match in matches}
    assert set(ALIASES) <= ids
    assert "common.style.pace_chaser" in ids
    assert "common.style.end_closer" in ids


def test_running_style_sequence_finding_resolves_only_after_all_canonical_aliases_exist(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    glossary.mkdir(parents=True)
    (glossary / "ui_community_terms.json").write_text(json.dumps(_community_terms(), ensure_ascii=False), encoding="utf-8")
    (glossary / "canonical_findings.json").write_text(json.dumps({
        "findings": [{
            "finding_id": FINDING_ID,
            "status": "open",
            "source_zh_cn": "领放][先行][居中][追赶",
            "match_mode": "contains",
            "source_paths": ["text_data_dict.json"],
            "suggested_targets_vi": [EXPECTED_TARGET],
            "canonical_resolution": None,
        }]
    }, ensure_ascii=False), encoding="utf-8")

    assert resolve(tmp_path) is False
    assert harden(tmp_path) is True
    assert resolve(tmp_path) is True
    assert resolve(tmp_path) is False
    finding = json.loads((glossary / "canonical_findings.json").read_text(encoding="utf-8"))["findings"][0]
    assert finding["canonical_resolution"] == {
        "layer": "context_guard",
        "term_id": "running_style.sequence",
        "target_vi": EXPECTED_TARGET,
    }

from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import refresh_canonical_resolutions
from scripts.harden_shooting_star_dioskouroi_finding import DECISION, TERM, harden


def _seed(tmp_path: Path) -> None:
    g = tmp_path / "glossary"; g.mkdir()
    for name, payload in [
        ("ui_community_terms.json", {"schema_version": 1, "terms": []}),
        ("terminology_reviews.json", {"schema_version": 1, "decisions": []}),
        ("source_bridge_terms.json", {"terms": []}),
        ("term_registry.json", {"terms": []}),
    ]:
        (g / name).write_text(json.dumps(payload), encoding="utf-8")


def _finding() -> dict:
    return {"finding_id":"cf-1740c7a1409d4821","status":"open","source_zh_cn":"狄俄斯库里的流星","match_mode":"contains","source_paths":["text_data_dict.json"],"key_exact":[],"json_path_prefixes":[["172"]],"suggested_targets_vi":[],"canonical_resolution":None,"review_resolution":None}


def test_global_title_resolves_finding(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False
    community = json.loads((tmp_path / "glossary" / "ui_community_terms.json").read_text(encoding="utf-8"))
    rule = next(x for x in community["terms"] if x["id"] == TERM["id"])
    assert rule["preferred"] == "Shooting Star of Dioskouroi"
    reviews = json.loads((tmp_path / "glossary" / "terminology_reviews.json").read_text(encoding="utf-8"))
    decision = next(x for x in reviews["decisions"] if x["decision_id"] == DECISION["decision_id"])
    assert decision["ja"] == ["ディオスクロイの流星"]
    finding = refresh_canonical_resolutions(tmp_path, {"schema_version":1,"findings":[_finding()]})["findings"][0]
    assert finding["canonical_resolution"] == {"layer":"community","term_id":"skill.admire_vega.shooting_star_of_dioskouroi","target_vi":"Shooting Star of Dioskouroi"}

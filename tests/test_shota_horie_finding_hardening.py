from __future__ import annotations
import json
from pathlib import Path
from scripts.canonical_findings import refresh_canonical_resolutions
from scripts.harden_shota_horie_finding import DECISION, TERM, harden


def _seed(tmp_path: Path) -> None:
    g=tmp_path/"glossary"; g.mkdir()
    (g/"ui_community_terms.json").write_text(json.dumps({"schema_version":1,"terms":[]}),encoding="utf-8")
    (g/"terminology_reviews.json").write_text(json.dumps({"schema_version":1,"decisions":[]}),encoding="utf-8")
    (g/"term_registry.json").write_text(json.dumps({"terms":[]}),encoding="utf-8")
    (g/"source_bridge_terms.json").write_text(json.dumps({"terms":[]}),encoding="utf-8")


def _finding(source_path: str="text_data_dict.json") -> dict:
    return {"finding_id":"cf-9912f84bf82c3999","status":"open","source_zh_cn":"堀江晶太","match_mode":"contains","source_paths":[source_path],"key_exact":[],"json_path_prefixes":[],"suggested_targets_vi":[],"canonical_resolution":None,"review_resolution":{"decision_id":"parallel.ctx-old.shota-horie-defer","action":"defer","target_vi":None}}


def test_hardener_resolves_shota_horie_and_is_idempotent(tmp_path: Path) -> None:
    _seed(tmp_path); assert harden(tmp_path) is True; assert harden(tmp_path) is False
    c=json.loads((tmp_path/"glossary"/"ui_community_terms.json").read_text(encoding="utf-8")); rule=next(x for x in c["terms"] if x["id"]==TERM["id"])
    assert rule["preferred"]=="Shota Horie" and rule["source_paths"]==["text_data_dict.json"]
    r=json.loads((tmp_path/"glossary"/"terminology_reviews.json").read_text(encoding="utf-8")); dec=next(x for x in r["decisions"] if x["decision_id"]==DECISION["decision_id"]); assert dec["target_vi"]=="Shota Horie"
    f=refresh_canonical_resolutions(tmp_path,{"schema_version":1,"findings":[_finding()]})["findings"][0]
    assert f["canonical_resolution"]=={"layer":"community","term_id":"proper_name.shota_horie","target_vi":"Shota Horie"}


def test_rule_does_not_cover_other_source_file(tmp_path: Path) -> None:
    _seed(tmp_path); assert harden(tmp_path) is True
    f=refresh_canonical_resolutions(tmp_path,{"schema_version":1,"findings":[_finding("localize_dict.json")]})["findings"][0]
    assert f["canonical_resolution"] is None

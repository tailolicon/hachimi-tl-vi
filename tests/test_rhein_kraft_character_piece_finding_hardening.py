from __future__ import annotations

import json
from pathlib import Path

from scripts.canonical_findings import active_findings, refresh_canonical_resolutions
from scripts.harden_rhein_kraft_character_piece_finding import DECISION_ID, FINDING_ID, RULE_ID, SOURCE_ZH, TARGET, harden


def _finding(prefix="113") -> dict:
    return {
        "finding_id": FINDING_ID,
        "status": "open",
        "source_zh_cn": SOURCE_ZH,
        "match_mode": "exact",
        "source_paths": ["text_data_dict.json"],
        "key_exact": [],
        "json_path_prefixes": [[prefix]],
        "suggested_targets_vi": [TARGET],
        "canonical_resolution": None,
        "review_resolution": None,
    }


def _seed(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"; glossary.mkdir(parents=True)
    payloads = {
        "ui_community_terms.json": {"schema_version": 1, "terms": []},
        "terminology_reviews.json": {"schema_version": 1, "decisions": []},
        "canonical_findings.json": {"schema_version": 1, "findings": [_finding()]},
        "term_registry.json": {"terms": []}, "source_bridge_terms.json": {"terms": []},
        "skill_name_style.json": {"canonical_examples": []},
    }
    for name,payload in payloads.items():
        (glossary/name).write_text(json.dumps(payload), encoding="utf-8")


def test_hardener_resolves_rhein_kraft_character_piece_and_is_idempotent(tmp_path: Path) -> None:
    _seed(tmp_path)
    assert harden(tmp_path) is True
    assert harden(tmp_path) is False
    community=json.loads((tmp_path/'glossary/ui_community_terms.json').read_text())
    rule=next(x for x in community['terms'] if x['id']==RULE_ID)
    assert rule['preferred']==TARGET and rule['json_path_prefixes']==[['113']] and rule['match_mode']=='exact'
    reviews=json.loads((tmp_path/'glossary/terminology_reviews.json').read_text())
    assert next(x for x in reviews['decisions'] if x['decision_id']==DECISION_ID)['target_vi']==TARGET
    ledger=json.loads((tmp_path/'glossary/canonical_findings.json').read_text())
    finding=refresh_canonical_resolutions(tmp_path, ledger)['findings'][0]
    assert finding['canonical_resolution']=={'layer':'community','term_id':RULE_ID,'target_vi':TARGET}
    assert finding['review_resolution']=={'decision_id':DECISION_ID,'action':'lock','target_vi':TARGET}
    assert active_findings({'findings':[finding]})==[]


def test_rule_is_scoped_to_character_piece_category(tmp_path: Path) -> None:
    _seed(tmp_path); assert harden(tmp_path) is True
    outside=_finding(prefix='114')
    resolved=refresh_canonical_resolutions(tmp_path, {'schema_version':1,'findings':[outside]})['findings'][0]
    assert resolved['canonical_resolution'] is None

from __future__ import annotations

import json

from scripts.translation_review_common import (
    context_snapshot_hash,
    item_scoped_context_hash,
    item_scoped_policy_hash,
)


def _write(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def test_terminology_changes_do_not_churn_global_context(tmp_path):
    glossary = tmp_path / "glossary"
    _write(glossary / "term_registry.json", {"terms": []})
    _write(glossary / "ui_community_terms.json", {"terms": []})
    before_context = context_snapshot_hash(tmp_path)
    before_policy = item_scoped_policy_hash(tmp_path)

    _write(glossary / "term_registry.json", {"terms": [{
        "id": "race.grade.g1",
        "zh_cn": ["GⅠ"],
        "target_vi": "G1",
        "locked": True,
    }]})

    assert context_snapshot_hash(tmp_path) == before_context
    assert item_scoped_policy_hash(tmp_path) != before_policy
    terms = json.loads((glossary / "term_registry.json").read_text())["terms"]
    assert item_scoped_context_hash(
        key=None,
        source="GⅠ",
        source_path="text_data_dict.json",
        json_path=["1", "1"],
        locked_terms=terms,
        community_terms=[],
    ) is not None
    assert item_scoped_context_hash(
        key=None,
        source="unrelated",
        source_path="text_data_dict.json",
        json_path=["1", "2"],
        locked_terms=terms,
        community_terms=[],
    ) is None


def test_canonical_findings_do_not_change_plan_policy_identity(tmp_path):
    glossary = tmp_path / "glossary"
    _write(glossary / "term_registry.json", {"terms": []})
    _write(glossary / "ui_community_terms.json", {"terms": []})
    _write(glossary / "canonical_findings.json", {"findings": []})
    before = item_scoped_policy_hash(tmp_path)

    _write(glossary / "canonical_findings.json", {"findings": [{
        "finding_id": "cf-test",
        "status": "open",
        "source_zh_cn": "测试",
        "match_mode": "exact",
    }]})

    assert item_scoped_policy_hash(tmp_path) == before

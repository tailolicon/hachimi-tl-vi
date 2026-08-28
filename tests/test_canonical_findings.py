from __future__ import annotations

import json

from scripts.canonical_findings import (
    active_findings,
    finding_matches_item,
    merge_worker_findings,
    normalize_worker_finding,
    refresh_canonical_resolutions,
)
from scripts.translation_review_common import item_scoped_policy_hash


def _item(source="相性奖励", key="Outgame0343"):
    return {
        "uid": "zhcn:test-affinity",
        "source_text": source,
        "source_path": "localize_dict.json",
        "json_path": [key],
        "key": key,
        "current_text": "Thưởng tương thích",
    }


def test_worker_finding_is_scoped_and_deduplicated():
    finding = normalize_worker_finding({
        "kind": "terminology",
        "source_zh_cn": "相性",
        "match_mode": "contains",
        "scope": "source_path",
        "suggested_target_vi": "Affinity",
        "concept": "Legacy Affinity",
        "reason": "Repeated Legacy UI concept needs one canonical label.",
        "confidence": "high",
    }, _item())
    assert finding is not None
    assert finding_matches_item(
        finding,
        key="Outgame0345",
        source="相性：◎",
        source_path="localize_dict.json",
        json_path=["Outgame0345"],
    )
    assert not finding_matches_item(
        finding,
        key=None,
        source="相性",
        source_path="story/data/test.json",
        json_path=["text"],
    )
    report = {
        "finding": finding,
        "uid": "zhcn:test-affinity",
        "plan_id": "p",
        "batch_id": "b",
        "claim_id": "c",
        "worker_id": "w",
        "source_path": "localize_dict.json",
        "json_path": ["Outgame0343"],
        "source_text": "相性奖励",
        "current_text": "Thưởng tương thích",
        "reported_at": "2026-08-28T00:00:00Z",
    }
    ledger = merge_worker_findings({"schema_version": 1, "findings": []}, [report, report])
    assert len(ledger["findings"]) == 1
    assert ledger["findings"][0]["evidence_count"] == 1
    assert ledger["findings"][0]["suggested_targets_vi"] == ["Affinity"]


def test_matching_canonical_rule_resolves_finding(tmp_path):
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    (glossary / "terminology_reviews.json").write_text("{}", encoding="utf-8")
    (glossary / "term_registry.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "source_bridge_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "ui_community_terms.json").write_text(json.dumps({
        "terms": [{
            "id": "common.legacy.affinity",
            "source_aliases": ["相性"],
            "preferred": "Affinity",
            "accepted": ["Affinity"],
            "source_paths": ["localize_dict.json"],
            "match_mode": "contains",
        }]
    }), encoding="utf-8")
    finding = normalize_worker_finding({
        "source_zh_cn": "相性",
        "match_mode": "contains",
        "scope": "source_path",
        "suggested_target_vi": "Affinity",
        "reason": "Legacy UI label",
        "confidence": "high",
    }, _item())
    ledger = {"schema_version": 1, "findings": [{
        **finding,
        "status": "open",
        "kinds": [finding["kind"]],
        "concepts": [],
        "suggested_targets_vi": [finding["suggested_target_vi"]],
        "confidence_levels": [finding["confidence"]],
        "reasons": [finding["reason"]],
        "evidence": [],
    }]}
    refreshed = refresh_canonical_resolutions(tmp_path, ledger)
    assert refreshed["findings"][0]["canonical_resolution"]["term_id"] == "common.legacy.affinity"
    assert active_findings(refreshed) == []


def test_conflicting_canonical_target_does_not_resolve_finding(tmp_path):
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    (glossary / "terminology_reviews.json").write_text("{}", encoding="utf-8")
    (glossary / "source_bridge_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "ui_community_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "term_registry.json").write_text(json.dumps({
        "terms": [{"id": "legacy.bad", "zh_cn": ["相性"], "target_vi": "Tương thích", "locked": True}]
    }), encoding="utf-8")
    finding = normalize_worker_finding({
        "source_zh_cn": "相性",
        "match_mode": "contains",
        "scope": "source_path",
        "suggested_target_vi": "Affinity",
        "reason": "Existing canonical target appears wrong in Legacy UI.",
        "confidence": "high",
    }, _item())
    ledger = {"schema_version": 1, "findings": [{
        **finding,
        "status": "open",
        "kinds": [finding["kind"]],
        "concepts": [],
        "suggested_targets_vi": [finding["suggested_target_vi"]],
        "confidence_levels": [finding["confidence"]],
        "reasons": [finding["reason"]],
        "evidence": [],
    }]}
    refreshed = refresh_canonical_resolutions(tmp_path, ledger)
    assert refreshed["findings"][0]["canonical_resolution"] is None
    assert len(active_findings(refreshed)) == 1


def test_finding_evidence_does_not_change_item_policy_hash(tmp_path):
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    for name, payload in {
        "term_registry.json": {"terms": []},
        "ui_community_terms.json": {"terms": []},
        "canonical_findings.json": {"findings": [{
            "finding_id": "cf-test",
            "status": "open",
            "source_zh_cn": "相性",
            "match_mode": "contains",
            "source_paths": ["localize_dict.json"],
            "key_exact": [],
            "json_path_prefixes": [],
            "suggested_targets_vi": ["Affinity"],
            "kinds": ["terminology"],
            "concepts": ["Legacy Affinity"],
            "evidence": [{"uid": "one"}],
            "evidence_count": 1,
        }]},
    }.items():
        (glossary / name).write_text(json.dumps(payload), encoding="utf-8")
    before = item_scoped_policy_hash(tmp_path)
    payload = json.loads((glossary / "canonical_findings.json").read_text(encoding="utf-8"))
    payload["findings"][0]["evidence"].append({"uid": "two"})
    payload["findings"][0]["evidence_count"] = 2
    (glossary / "canonical_findings.json").write_text(json.dumps(payload), encoding="utf-8")
    assert item_scoped_policy_hash(tmp_path) == before

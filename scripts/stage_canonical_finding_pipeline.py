from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_exact(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        if new in text:
            return
        raise SystemExit(f"expected patch anchor not found in {path}: {old[:120]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8", newline="\n")


def append_before(path: Path, marker: str, addition: str) -> None:
    text = path.read_text(encoding="utf-8")
    if addition.strip() in text:
        return
    if marker not in text:
        raise SystemExit(f"append marker not found in {path}: {marker!r}")
    path.write_text(text.replace(marker, addition + "\n\n" + marker, 1), encoding="utf-8", newline="\n")


canonical_script = r'''from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FINDINGS = ROOT / "glossary/canonical_findings.json"
DEFAULT_REVIEWS = ROOT / "glossary/terminology_reviews.json"
ALLOWED_KINDS = {"terminology", "proper_name", "source_bridge", "context_rule", "system_label"}
ALLOWED_CONFIDENCE = {"high", "medium", "low"}
BLOCKING_STATUSES = {"open", "deferred"}
MAX_EVIDENCE = 24


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return default
    return json.loads(text)


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def _strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value] if value else []
    if isinstance(value, list):
        return [str(item) for item in value if str(item)]
    return []


def _norm(value: Any) -> str:
    return " ".join(str(value).casefold().split())


def _source_matches(source: str, alias: str, mode: str) -> bool:
    if not alias:
        return False
    if mode == "exact":
        return source.strip() == alias.strip()
    if source == alias:
        return True
    return len(alias) >= 2 and alias in source


def _path_prefix_matches(path: list[Any] | None, raw_prefixes: Any) -> bool:
    if not raw_prefixes:
        return True
    if not isinstance(path, list):
        return False
    normalized = [str(value) for value in path]
    for raw in raw_prefixes:
        values = raw if isinstance(raw, list) else [raw]
        prefix = [str(value) for value in values]
        if normalized[: len(prefix)] == prefix:
            return True
    return False


def finding_matches_item(
    finding: dict[str, Any],
    *,
    key: str | None,
    source: str,
    source_path: str | None,
    json_path: list[Any] | None,
) -> bool:
    source_paths = _strings(finding.get("source_paths"))
    if source_paths and (source_path is None or source_path not in source_paths):
        return False
    exact_keys = _strings(finding.get("key_exact"))
    if exact_keys and (key is None or key not in exact_keys):
        return False
    if not _path_prefix_matches(json_path, finding.get("json_path_prefixes", [])):
        return False
    alias = str(finding.get("source_zh_cn") or "").strip()
    return _source_matches(source, alias, str(finding.get("match_mode") or "exact"))


def active_findings(payload: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not isinstance(payload, dict):
        return []
    result: list[dict[str, Any]] = []
    for finding in payload.get("findings", []):
        if not isinstance(finding, dict):
            continue
        if str(finding.get("status") or "open") not in BLOCKING_STATUSES:
            continue
        if finding.get("canonical_resolution"):
            continue
        review = finding.get("review_resolution")
        if isinstance(review, dict) and str(review.get("action") or "") == "ignore":
            continue
        result.append(finding)
    return result


def finding_semantic_view(finding: dict[str, Any]) -> dict[str, Any]:
    review = finding.get("review_resolution") if isinstance(finding.get("review_resolution"), dict) else {}
    return {
        "finding_id": str(finding.get("finding_id") or ""),
        "status": str(finding.get("status") or "open"),
        "source_zh_cn": str(finding.get("source_zh_cn") or ""),
        "match_mode": str(finding.get("match_mode") or "exact"),
        "source_paths": _strings(finding.get("source_paths")),
        "key_exact": _strings(finding.get("key_exact")),
        "json_path_prefixes": finding.get("json_path_prefixes", []),
        "suggested_targets_vi": sorted(set(_strings(finding.get("suggested_targets_vi")))),
        "concepts": sorted(set(_strings(finding.get("concepts")))),
        "kinds": sorted(set(_strings(finding.get("kinds")))),
        "review_action": str(review.get("action") or ""),
        "review_target_vi": str(review.get("target_vi") or ""),
    }


def _finding_id(payload: dict[str, Any]) -> str:
    semantic = {
        "source_zh_cn": payload["source_zh_cn"],
        "match_mode": payload["match_mode"],
        "source_paths": payload.get("source_paths", []),
        "key_exact": payload.get("key_exact", []),
        "json_path_prefixes": payload.get("json_path_prefixes", []),
    }
    encoded = json.dumps(semantic, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "cf-" + hashlib.sha256(encoded).hexdigest()[:16]


def normalize_worker_finding(raw: Any, item: dict[str, Any]) -> dict[str, Any] | None:
    if raw is None:
        return None
    if not isinstance(raw, dict):
        raise ValueError("canonical_finding must be an object")
    kind = str(raw.get("kind") or "terminology").strip().lower()
    if kind not in ALLOWED_KINDS:
        raise ValueError(f"unsupported canonical_finding kind {kind!r}")
    confidence = str(raw.get("confidence") or "").strip().lower()
    if confidence not in ALLOWED_CONFIDENCE:
        raise ValueError("canonical_finding confidence must be high, medium, or low")
    reason = str(raw.get("reason") or "").strip()
    if not reason:
        raise ValueError("canonical_finding reason is required")

    item_source = str(item.get("source_text") or "")
    source = str(raw.get("source_zh_cn") or item_source).strip()
    if not source:
        raise ValueError("canonical_finding source_zh_cn is required")
    requested_mode = str(raw.get("match_mode") or "").strip().lower()
    match_mode = requested_mode or ("exact" if source == item_source.strip() else "contains")
    if match_mode not in {"exact", "contains"}:
        raise ValueError("canonical_finding match_mode must be exact or contains")
    if match_mode == "exact" and source != item_source.strip():
        raise ValueError("exact canonical_finding source_zh_cn must equal the reviewed source text")
    if match_mode == "contains" and (len(source) < 2 or source not in item_source):
        raise ValueError("contains canonical_finding source_zh_cn must be a 2+ character substring of the reviewed source")

    source_path = str(item.get("source_path") or "").strip()
    if not source_path:
        raise ValueError("review item source_path is required for canonical_finding scope")
    json_path = item.get("json_path") if isinstance(item.get("json_path"), list) else []
    key = str(item.get("key") or "").strip()
    scope = str(raw.get("scope") or "auto").strip().lower()
    if scope not in {"auto", "item", "category", "source_path"}:
        raise ValueError("canonical_finding scope must be auto, item, category, or source_path")

    key_exact: list[str] = []
    json_prefixes: list[list[str]] = []
    if scope == "item":
        if key:
            key_exact = [key]
        elif json_path:
            json_prefixes = [[str(value) for value in json_path]]
    elif scope == "category":
        if source_path == "text_data_dict.json" and json_path:
            json_prefixes = [[str(json_path[0])]]
        elif key:
            key_exact = [key]
        elif json_path:
            json_prefixes = [[str(json_path[0])]]
    elif scope == "auto":
        if source_path == "text_data_dict.json" and json_path:
            json_prefixes = [[str(json_path[0])]]
        elif source_path == "localize_dict.json" and match_mode == "contains" and key:
            key_exact = [key]
        elif source_path != "localize_dict.json" and json_path:
            json_prefixes = [[str(json_path[0])]]

    result: dict[str, Any] = {
        "source_zh_cn": source,
        "match_mode": match_mode,
        "source_paths": [source_path],
        "key_exact": key_exact,
        "json_path_prefixes": json_prefixes,
        "kind": kind,
        "confidence": confidence,
        "reason": reason,
    }
    concept = str(raw.get("concept") or "").strip()
    if concept:
        result["concept"] = concept
    suggested = str(raw.get("suggested_target_vi") or "").strip()
    if suggested:
        result["suggested_target_vi"] = suggested
    result["finding_id"] = _finding_id(result)
    return result


def _add_unique(values: list[str], value: str) -> None:
    if value and value not in values:
        values.append(value)


def merge_worker_findings(ledger: dict[str, Any] | None, reports: list[dict[str, Any]]) -> dict[str, Any]:
    if not isinstance(ledger, dict):
        ledger = {}
    result = dict(ledger)
    result.setdefault("schema_version", 1)
    result.setdefault("policy", {
        "canonical": False,
        "rule": "Worker findings are blocking review evidence, never automatic canonical locks.",
        "resolution": "A finding stops blocking only after matching canonical context resolves it or an explicit ignore decision is recorded.",
    })
    rows = [row for row in result.get("findings", []) if isinstance(row, dict)]
    by_id = {str(row.get("finding_id") or ""): row for row in rows if row.get("finding_id")}

    for report in reports:
        finding = report.get("finding")
        if not isinstance(finding, dict):
            continue
        fid = str(finding.get("finding_id") or "")
        if not fid:
            continue
        row = by_id.get(fid)
        if row is None:
            row = {
                "finding_id": fid,
                "status": "open",
                "source_zh_cn": finding["source_zh_cn"],
                "match_mode": finding["match_mode"],
                "source_paths": finding.get("source_paths", []),
                "key_exact": finding.get("key_exact", []),
                "json_path_prefixes": finding.get("json_path_prefixes", []),
                "kinds": [],
                "concepts": [],
                "suggested_targets_vi": [],
                "confidence_levels": [],
                "reasons": [],
                "evidence_count": 0,
                "evidence": [],
                "canonical_resolution": None,
                "review_resolution": None,
                "first_seen_at": str(report.get("reported_at") or ""),
                "last_seen_at": str(report.get("reported_at") or ""),
            }
            rows.append(row)
            by_id[fid] = row
        _add_unique(row.setdefault("kinds", []), str(finding.get("kind") or ""))
        _add_unique(row.setdefault("concepts", []), str(finding.get("concept") or ""))
        _add_unique(row.setdefault("suggested_targets_vi", []), str(finding.get("suggested_target_vi") or ""))
        _add_unique(row.setdefault("confidence_levels", []), str(finding.get("confidence") or ""))
        _add_unique(row.setdefault("reasons", []), str(finding.get("reason") or ""))
        reported_at = str(report.get("reported_at") or "")
        if reported_at:
            if not row.get("first_seen_at"):
                row["first_seen_at"] = reported_at
            row["last_seen_at"] = reported_at

        evidence = {
            "uid": str(report.get("uid") or ""),
            "plan_id": str(report.get("plan_id") or ""),
            "batch_id": str(report.get("batch_id") or ""),
            "claim_id": str(report.get("claim_id") or ""),
            "worker_id": str(report.get("worker_id") or ""),
            "source_path": str(report.get("source_path") or ""),
            "json_path": report.get("json_path", []),
            "source_text": str(report.get("source_text") or ""),
            "current_text": str(report.get("current_text") or ""),
            "proposed_text": report.get("proposed_text"),
            "reported_at": reported_at,
        }
        evidence_key = (evidence["uid"], evidence["batch_id"], evidence["claim_id"])
        existing_keys = {
            (str(item.get("uid") or ""), str(item.get("batch_id") or ""), str(item.get("claim_id") or ""))
            for item in row.setdefault("evidence", []) if isinstance(item, dict)
        }
        if evidence_key not in existing_keys:
            row["evidence_count"] = int(row.get("evidence_count", 0)) + 1
            if len(row["evidence"]) < MAX_EVIDENCE:
                row["evidence"].append(evidence)

    rows.sort(key=lambda row: str(row.get("finding_id") or ""))
    result["findings"] = rows
    return result


def _latest_review_decisions(reviews: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for decision in reviews.get("decisions", []) if isinstance(reviews, dict) else []:
        if not isinstance(decision, dict):
            continue
        source = str(decision.get("source_zh_cn") or "").strip()
        action = str(decision.get("action") or "").strip().lower()
        if source and action in {"lock", "defer", "ignore"}:
            result[source] = decision
    return result


def _prefix_covers(rule_prefix: list[str], finding_prefix: list[str]) -> bool:
    return finding_prefix[: len(rule_prefix)] == rule_prefix


def _rule_covers_finding(rule: dict[str, Any], finding: dict[str, Any]) -> bool:
    finding_paths = _strings(finding.get("source_paths"))
    rule_paths = _strings(rule.get("source_paths"))
    if rule_paths and any(path not in rule_paths for path in finding_paths):
        return False

    finding_keys = _strings(finding.get("key_exact"))
    rule_keys = _strings(rule.get("key_exact"))
    rule_prefixes = _strings(rule.get("key_prefixes"))
    if finding_keys:
        if rule_keys and any(key not in rule_keys for key in finding_keys):
            return False
        if not rule_keys and rule_prefixes and any(not any(key.startswith(prefix) for prefix in rule_prefixes) for key in finding_keys):
            return False
    elif rule_keys or rule_prefixes:
        return False

    finding_prefixes = [
        [str(value) for value in (raw if isinstance(raw, list) else [raw])]
        for raw in finding.get("json_path_prefixes", [])
    ]
    rule_json_prefixes = [
        [str(value) for value in (raw if isinstance(raw, list) else [raw])]
        for raw in rule.get("json_path_prefixes", [])
    ]
    if finding_prefixes:
        if rule_json_prefixes and any(
            not any(_prefix_covers(rule_prefix, finding_prefix) for rule_prefix in rule_json_prefixes)
            for finding_prefix in finding_prefixes
        ):
            return False
    elif rule_json_prefixes:
        return False
    return True


def _rule_matches_finding_source(rule: dict[str, Any], alias_field: str, finding: dict[str, Any]) -> bool:
    source = str(finding.get("source_zh_cn") or "")
    mode = str(rule.get("match_mode") or "contains")
    return any(_source_matches(source, alias, mode) for alias in _strings(rule.get(alias_field)))


def _rule_target_forms(rule: dict[str, Any], layer: str) -> list[str]:
    if layer == "locked":
        return _strings(rule.get("target_vi"))
    return list(dict.fromkeys(
        _strings(rule.get("preferred"))
        + _strings(rule.get("accepted"))
        + _strings(rule.get("compact"))
    ))


def refresh_canonical_resolutions(repo_root: Path, ledger: dict[str, Any] | None = None) -> dict[str, Any]:
    if ledger is None:
        ledger = read_json(repo_root / "glossary/canonical_findings.json", {}) or {}
    result = dict(ledger) if isinstance(ledger, dict) else {"schema_version": 1, "findings": []}
    reviews = read_json(repo_root / "glossary/terminology_reviews.json", {}) or {}
    decisions = _latest_review_decisions(reviews if isinstance(reviews, dict) else {})

    registry = read_json(repo_root / "glossary/term_registry.json", {}) or {}
    community = read_json(repo_root / "glossary/ui_community_terms.json", {}) or {}
    bridge = read_json(repo_root / "glossary/source_bridge_terms.json", {}) or {}
    rules: list[tuple[str, dict[str, Any], str]] = []
    for term in registry.get("terms", []) if isinstance(registry, dict) else []:
        if isinstance(term, dict) and bool(term.get("locked")):
            rules.append(("locked", term, "zh_cn"))
    for term in community.get("terms", []) if isinstance(community, dict) else []:
        if isinstance(term, dict):
            rules.append(("community", term, "source_aliases"))
    for term in bridge.get("terms", []) if isinstance(bridge, dict) else []:
        if isinstance(term, dict):
            rules.append(("source_bridge", term, "zh_cn"))

    for finding in result.get("findings", []) if isinstance(result.get("findings"), list) else []:
        if not isinstance(finding, dict):
            continue
        decision = decisions.get(str(finding.get("source_zh_cn") or ""))
        finding["review_resolution"] = (
            {
                "decision_id": decision.get("decision_id"),
                "action": str(decision.get("action") or "").strip().lower(),
                "target_vi": decision.get("target_vi"),
            }
            if isinstance(decision, dict)
            else None
        )
        finding["canonical_resolution"] = None
        if str(finding.get("status") or "open") not in BLOCKING_STATUSES:
            continue
        if isinstance(finding.get("review_resolution"), dict) and finding["review_resolution"].get("action") == "ignore":
            continue

        expected = set(_norm(value) for value in _strings(finding.get("suggested_targets_vi")) if _norm(value))
        review_resolution = finding.get("review_resolution")
        if not expected and isinstance(review_resolution, dict) and review_resolution.get("action") == "lock":
            target = str(review_resolution.get("target_vi") or "").strip()
            if target:
                expected.add(_norm(target))
        if len(expected) != 1:
            continue

        for layer, rule, alias_field in rules:
            if not _rule_covers_finding(rule, finding):
                continue
            if not _rule_matches_finding_source(rule, alias_field, finding):
                continue
            forms = {_norm(value) for value in _rule_target_forms(rule, layer) if _norm(value)}
            if not forms.intersection(expected):
                continue
            finding["canonical_resolution"] = {
                "layer": layer,
                "term_id": str(rule.get("id") or ""),
                "target_vi": next((value for value in _rule_target_forms(rule, layer) if _norm(value) in expected), ""),
            }
            break
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Refresh canonical-finding resolution state without auto-locking terminology.")
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--findings", type=Path, default=None)
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    path = args.findings or repo_root / "glossary/canonical_findings.json"
    ledger = read_json(path, {"schema_version": 1, "findings": []}) or {"schema_version": 1, "findings": []}
    if args.refresh:
        ledger = refresh_canonical_resolutions(repo_root, ledger)
        write_json(path, ledger)
    active = active_findings(ledger)
    print(f"findings={len(ledger.get('findings', []))} active={len(active)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''

finding_test = r'''from __future__ import annotations

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
'''

(ROOT / "scripts/canonical_findings.py").write_text(canonical_script, encoding="utf-8", newline="\n")
(ROOT / "tests/test_canonical_findings.py").write_text(finding_test, encoding="utf-8", newline="\n")
findings_path = ROOT / "glossary/canonical_findings.json"
if not findings_path.exists():
    findings_path.write_text(json.dumps({
        "schema_version": 1,
        "policy": {
            "canonical": False,
            "rule": "Worker findings are blocking review evidence, never automatic canonical locks.",
            "resolution": "A finding stops blocking only after matching canonical context resolves it or an explicit ignore decision is recorded."
        },
        "findings": []
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")

path = ROOT / "scripts/translation_review_common.py"
replace_exact(path, 'from typing import Any\n\n# Letters/ideographs only;', 'from typing import Any\n\ntry:\n    from scripts.canonical_findings import active_findings, finding_matches_item, finding_semantic_view\nexcept ModuleNotFoundError:\n    from canonical_findings import active_findings, finding_matches_item, finding_semantic_view  # type: ignore[no-redef]\n\n# Letters/ideographs only;')
replace_exact(path, 'SOURCE_BRIDGE_PATHS = (SOURCE_BRIDGE_PATH, SOURCE_BRIDGE_GENERATED_PATH)\n', 'SOURCE_BRIDGE_PATHS = (SOURCE_BRIDGE_PATH, SOURCE_BRIDGE_GENERATED_PATH)\nCANONICAL_FINDINGS_PATH = "glossary/canonical_findings.json"\n')
replace_exact(path, '    encoded = json.dumps(semantic, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")\n    return hashlib.sha256(encoded).hexdigest()\n\n\ndef source_bridge_policy_hash', '    finding_payload = load_json(repo_root / CANONICAL_FINDINGS_PATH, {}) or {}\n    semantic[CANONICAL_FINDINGS_PATH] = sorted(\n        [finding_semantic_view(finding) for finding in active_findings(finding_payload)],\n        key=lambda finding: str(finding.get("finding_id", "")),\n    )\n    encoded = json.dumps(semantic, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")\n    return hashlib.sha256(encoded).hexdigest()\n\n\ndef source_bridge_policy_hash')
replace_exact(path, '    community_terms: list[dict[str, Any]],\n) -> str | None:\n', '    community_terms: list[dict[str, Any]],\n    canonical_findings: list[dict[str, Any]] | None = None,\n) -> str | None:\n')
replace_exact(path, '            matched.append({"layer": layer, "term": term})\n    if not matched:\n', '            matched.append({"layer": layer, "term": term})\n    for finding in canonical_findings or []:\n        matched.append({"layer": "canonical_finding", "term": finding_semantic_view(finding)})\n    if not matched:\n')
append_before(path, 'def load_source_bridge_config(repo_root: Path) -> dict[str, Any]:', '''def load_canonical_findings(repo_root: Path) -> list[dict[str, Any]]:\n    payload = load_json(repo_root / CANONICAL_FINDINGS_PATH, {"findings": []}) or {}\n    return active_findings(payload if isinstance(payload, dict) else {})\n\n\ndef canonical_finding_matches(\n    key: str | None,\n    source: str,\n    findings: list[dict[str, Any]],\n    *,\n    source_path: str | None = None,\n    json_path: list[Any] | None = None,\n) -> list[dict[str, Any]]:\n    result: list[dict[str, Any]] = []\n    for finding in findings:\n        if finding_matches_item(\n            finding, key=key, source=source, source_path=source_path, json_path=json_path\n        ):\n            result.append(finding_semantic_view(finding))\n    return result''')

path = ROOT / "scripts/build_translation_review_plan.py"
replace_exact(path, '        community_term_matches,\n        context_snapshot_hash,\n', '        canonical_finding_matches,\n        community_term_matches,\n        context_snapshot_hash,\n')
replace_exact(path, '        community_term_matches,\n        context_snapshot_hash,\n', '        canonical_finding_matches,\n        community_term_matches,\n        context_snapshot_hash,\n')
replace_exact(path, '        load_community_terms,\n        load_json,\n', '        load_canonical_findings,\n        load_community_terms,\n        load_json,\n')
replace_exact(path, '        load_community_terms,\n        load_json,\n', '        load_canonical_findings,\n        load_community_terms,\n        load_json,\n')
replace_exact(path, '    community_terms = load_community_terms(repo_root)\n    skill_examples = load_skill_examples(repo_root)\n', '    community_terms = load_community_terms(repo_root)\n    canonical_findings = load_canonical_findings(repo_root)\n    skill_examples = load_skill_examples(repo_root)\n')
replace_exact(path, '            bridge_risks = source_bridge_risk_matches(source, bridge_risk_rules)\n            bridge_sensitive = bool(bridge_terms or bridge_risks)\n', '            bridge_risks = source_bridge_risk_matches(source, bridge_risk_rules)\n            finding_matches = canonical_finding_matches(\n                key, source, canonical_findings, source_path=source_file, json_path=json_path\n            )\n            bridge_sensitive = bool(bridge_terms or bridge_risks)\n')
replace_exact(path, '                locked_terms=locked_terms,\n                community_terms=community_terms,\n            )\n\n            prior =', '                locked_terms=locked_terms,\n                community_terms=community_terms,\n                canonical_findings=finding_matches,\n            )\n\n            prior =')
replace_exact(path, '            )\n            candidates.append({\n                "uid": uid,', '            )\n            if finding_matches:\n                flags = list(dict.fromkeys([*flags, "canonical_finding"]))\n                score += 40\n            candidates.append({\n                "uid": uid,')
replace_exact(path, '                "source_bridge_policy_sha256": bridge_hash if bridge_sensitive else None,\n                "item_context_sha256": item_context_hash,\n', '                "source_bridge_policy_sha256": bridge_hash if bridge_sensitive else None,\n                "canonical_findings": finding_matches,\n                "item_context_sha256": item_context_hash,\n')

path = ROOT / "scripts/merge_translation_review.py"
replace_exact(path, 'from hachimi_tl_vi.parallel import set_json_path, structural_qa\n\ntry:\n', 'from hachimi_tl_vi.parallel import set_json_path, structural_qa\n\ntry:\n    from scripts.canonical_findings import active_findings, finding_matches_item, merge_worker_findings, normalize_worker_finding, refresh_canonical_resolutions\nexcept ModuleNotFoundError:\n    from canonical_findings import active_findings, finding_matches_item, merge_worker_findings, normalize_worker_finding, refresh_canonical_resolutions  # type: ignore[no-redef]\n\ntry:\n')
replace_exact(path, '        if not isinstance(reason, str) or not reason.strip():\n            errors.append(f"{uid}: reason is required")\n        if action == "revise" and confidence == "low":\n', '        if not isinstance(reason, str) or not reason.strip():\n            errors.append(f"{uid}: reason is required")\n        canonical_finding = None\n        if decision.get("canonical_finding") is not None:\n            try:\n                canonical_finding = normalize_worker_finding(decision.get("canonical_finding"), item)\n            except ValueError as exc:\n                errors.append(f"{uid}: {exc}")\n        if action == "revise" and confidence == "low":\n')
replace_exact(path, '            "speech_basis": decision.get("speech_basis"),\n            "auto_defer_reasons": auto_defer,\n', '            "speech_basis": decision.get("speech_basis"),\n            "canonical_finding": canonical_finding,\n            "auto_defer_reasons": auto_defer,\n')
append_before(path, 'def merge(repo_root: Path) -> dict[str, Any]:', '''def _defer_for_open_findings(decisions: list[dict[str, Any]], findings: list[dict[str, Any]]) -> None:\n    if not findings:\n        return\n    for decision in decisions:\n        if decision.get("action") not in {"keep", "revise"}:\n            continue\n        item = decision["item"]\n        matches = [finding for finding in findings if finding_matches_item(\n            finding, key=item.get("key"), source=str(item.get("source_text", "")),\n            source_path=item.get("source_path"), json_path=item.get("json_path"),\n        )]\n        if not matches:\n            continue\n        decision["action"] = "defer"\n        reasons = decision.setdefault("auto_defer_reasons", [])\n        if "open_canonical_finding" not in reasons:\n            reasons.append("open_canonical_finding")\n        decision["canonical_findings"] = [str(row.get("finding_id") or "") for row in matches]\n''')
replace_exact(path, '    docs: dict[str, Any] = {}\n    dirty_docs: set[str] = set()\n\n    report:', '    docs: dict[str, Any] = {}\n    dirty_docs: set[str] = set()\n    findings_path = repo_root / "glossary/canonical_findings.json"\n    findings_ledger = load_json(findings_path, {"schema_version": 1, "findings": []}) or {"schema_version": 1, "findings": []}\n    findings_ledger = refresh_canonical_resolutions(repo_root, findings_ledger)\n    runtime_findings = active_findings(findings_ledger)\n\n    report:')
replace_exact(path, '        "auto_deferred": [],\n    }\n', '        "auto_deferred": [],\n        "canonical_findings_reported": [],\n    }\n')
replace_exact(path, '        if errors:\n            raise ValueError(f"{batch_id}: " + "; ".join(errors))\n\n        stale:', '        if errors:\n            raise ValueError(f"{batch_id}: " + "; ".join(errors))\n\n        batch_finding_reports: list[dict[str, Any]] = []\n        for decision in decisions:\n            finding = decision.get("canonical_finding")\n            if not isinstance(finding, dict):\n                continue\n            item = decision["item"]\n            batch_finding_reports.append({\n                "finding": finding, "uid": decision["uid"], "plan_id": plan_id, "batch_id": batch_id,\n                "claim_id": claim_id, "worker_id": completion.get("worker_id"), "source_path": item.get("source_path"),\n                "json_path": item.get("json_path"), "source_text": item.get("source_text"), "current_text": item.get("current_text"),\n                "proposed_text": decision.get("proposed_text"), "reported_at": result.get("reviewed_at") or completion.get("completed_at") or utc_now(),\n            })\n        if batch_finding_reports:\n            findings_ledger = merge_worker_findings(findings_ledger, batch_finding_reports)\n            findings_ledger = refresh_canonical_resolutions(repo_root, findings_ledger)\n            runtime_findings = active_findings(findings_ledger)\n            report["canonical_findings_reported"].extend(sorted({str(row["finding"].get("finding_id") or "") for row in batch_finding_reports}))\n        _defer_for_open_findings(decisions, runtime_findings)\n\n        stale:')
replace_exact(path, '    write_json(reviewed_path, reviewed)\n', '    findings_ledger = refresh_canonical_resolutions(repo_root, findings_ledger)\n    write_json(findings_path, findings_ledger)\n    write_json(reviewed_path, reviewed)\n')

path = ROOT / "scripts/build_terminology_review_queue.py"
replace_exact(path, 'from typing import Any\n\nROOT =', 'from typing import Any\n\ntry:\n    from scripts.canonical_findings import active_findings\nexcept ModuleNotFoundError:\n    from canonical_findings import active_findings  # type: ignore[no-redef]\n\nROOT =')
replace_exact(path, 'DEFAULT_REVIEWS = ROOT / "glossary/terminology_reviews.json"\nDEFAULT_OUTPUT', 'DEFAULT_REVIEWS = ROOT / "glossary/terminology_reviews.json"\nDEFAULT_FINDINGS = ROOT / "glossary/canonical_findings.json"\nDEFAULT_OUTPUT')
replace_exact(path, 'KIND_PRIORITY = {\n    "skill_name": 900,', 'KIND_PRIORITY = {\n    "canonical_finding": 950,\n    "skill_name": 900,')
replace_exact(path, '    reviews: dict[str, Any] | None = None,\n) -> dict[str, Any]:', '    reviews: dict[str, Any] | None = None,\n    findings: dict[str, Any] | None = None,\n) -> dict[str, Any]:')
replace_exact(path, '    queue: list[dict[str, Any]] = []\n    status_counts:', '    finding_map: dict[str, list[dict[str, Any]]] = defaultdict(list)\n    for finding in active_findings(findings or {}):\n        source = str(finding.get("source_zh_cn") or "").strip()\n        if not source:\n            continue\n        row = grouped.setdefault(source, {"source_zh_cn": source, "kinds": set(), "locators": [], "candidate_ids": []})\n        row["kinds"].add("canonical_finding")\n        finding_map[source].append(finding)\n\n    queue: list[dict[str, Any]] = []\n    status_counts:')
replace_exact(path, '        if locked:\n            status = "canonical_locked"\n            priority = 0\n            reason = "Already covered by locked term_registry."\n        elif decision_action == "defer":', '        finding_rows = finding_map.get(source, [])\n\n        if decision_action == "defer":')
replace_exact(path, '            priority = 12000 + base\n            reason = "Explicit lock decision exists but the canonical registry does not contain it yet."\n        elif conflict:', '            priority = 17000 + base\n            reason = "Explicit lock decision exists but the canonical registry does not contain it yet."\n        elif finding_rows:\n            status = "canonical_finding_review"\n            priority = 15000 + base\n            reason = "A translation-review worker reported a systemic canonical finding; resolve it before matching entries are accepted."\n        elif locked:\n            status = "canonical_locked"\n            priority = 0\n            reason = "Already covered by locked term_registry."\n        elif conflict:')
replace_exact(path, '        queue.append(output)\n        status_counts[status] += 1\n', '        if finding_rows:\n            output["canonical_findings"] = [{\n                "finding_id": row.get("finding_id"), "suggested_targets_vi": row.get("suggested_targets_vi", []),\n                "concepts": row.get("concepts", []), "confidence_levels": row.get("confidence_levels", []),\n                "evidence_count": row.get("evidence_count", 0),\n            } for row in finding_rows]\n        queue.append(output)\n        status_counts[status] += 1\n')
replace_exact(path, '        "pending_lock_application",\n        "conflict_review",', '        "pending_lock_application",\n        "canonical_finding_review",\n        "conflict_review",')
replace_exact(path, '"priority_order": "unapplied explicit locks > conflicts > unresolved character identities > observed promotion candidates > untranslated skill/race/scenario/support entities."', '"priority_order": "unapplied explicit locks > worker-reported canonical findings > conflicts > unresolved character identities > observed promotion candidates > untranslated skill/race/scenario/support entities."')
replace_exact(path, '            "explicit_review_decisions": len(decisions),\n            "status_counts":', '            "explicit_review_decisions": len(decisions),\n            "open_canonical_findings": sum(len(rows) for rows in finding_map.values()),\n            "status_counts":')
replace_exact(path, '    parser.add_argument("--reviews", type=Path, default=DEFAULT_REVIEWS)\n    parser.add_argument("--output"', '    parser.add_argument("--reviews", type=Path, default=DEFAULT_REVIEWS)\n    parser.add_argument("--findings", type=Path, default=DEFAULT_FINDINGS)\n    parser.add_argument("--output"')
replace_exact(path, '    reviews = read_json(args.reviews, {}) or {}\n    if not all(isinstance(value, dict) for value in (generated, observed, registry, characters, reviews)):\n        raise SystemExit("all terminology review inputs must be JSON objects")\n\n    queue = build_queue(generated, observed, registry, characters, reviews)', '    reviews = read_json(args.reviews, {}) or {}\n    findings = read_json(args.findings, {}) or {}\n    if not all(isinstance(value, dict) for value in (generated, observed, registry, characters, reviews, findings)):\n        raise SystemExit("all terminology review inputs must be JSON objects")\n\n    queue = build_queue(generated, observed, registry, characters, reviews, findings)')

path = ROOT / "tests/test_terminology_review.py"
append_before(path, 'def test_explicit_lock_stays_high_priority_until_registry_application():', '''def test_worker_canonical_finding_is_actionable_even_with_conflicting_locked_term():\n    generated = {"total": 1, "candidates": [candidate("race_name", "相性")]}\n    registry = {"terms": [{"id": "legacy.bad", "zh_cn": ["相性"], "target_vi": "Tương thích", "locked": True}]}\n    findings = {"findings": [{"finding_id": "cf-affinity", "status": "open", "source_zh_cn": "相性", "match_mode": "exact", "source_paths": ["localize_dict.json"], "suggested_targets_vi": ["Affinity"], "canonical_resolution": None, "review_resolution": None, "evidence_count": 2}]}\n    result = build_queue(generated, {}, registry, {"characters": {}}, {}, findings)\n    row = result["review_queue"][0]\n    assert row["status"] == "canonical_finding_review"\n    assert row["canonical_findings"][0]["finding_id"] == "cf-affinity"\n''')

path = ROOT / "TRANSLATION_REVIEW.md"
replace_exact(path, '- `source_bridge_risks`\n\nUse embedded data first.', '- `source_bridge_risks`\n- `canonical_findings` — open systemic findings that block matching entries until canonical context is resolved\n\nUse embedded data first.')
append_before(path, '## Checkpoint loop', '''## Canonical-first discovery\n\nIf an item reveals a reusable/systemic terminology, proper-name, source-bridge, context-rule, or system-label problem that is not already safely canonicalized, do not establish a one-off translation and move on. Attach a `canonical_finding` to the decision and normally `defer` the item until canonical maintenance resolves it.\n\n```json\n"canonical_finding": {\n  "kind": "terminology|proper_name|source_bridge|context_rule|system_label",\n  "source_zh_cn": "相性",\n  "suggested_target_vi": "Affinity",\n  "concept": "Legacy Affinity",\n  "match_mode": "contains",\n  "scope": "source_path",\n  "reason": "Repeated player-facing concept needs one canonical label.",\n  "confidence": "high"\n}\n```\n\nUse the smallest alias that actually identifies the concept. Default to exact matching; use `contains` only for a clearly reusable concept. Prefer `scope=auto`; broaden to `source_path` only with strong evidence. Omit `suggested_target_vi` rather than guess. Isolated naturalness fixes are not canonical findings.\n\nThe merge pipeline deduplicates findings into `glossary/canonical_findings.json`. That ledger is evidence, not canonical. Open findings are item-scoped blocking context, are pushed near the top of the terminology-review queue, and normalize matching `keep`/`revise` decisions to `defer`. When matching canonical context lands, resolution refresh unblocks the finding and affected entries reopen under the new canonical context. Explicit `ignore` unblocks; explicit `defer` remains blocking.\n''')
replace_exact(path, '      "speech_basis": "when applicable",\n      "confidence": "high|medium|low"', '      "speech_basis": "when applicable",\n      "canonical_finding": "optional systemic finding object",\n      "confidence": "high|medium|low"')
replace_exact(path, '- canonical glossary/speech files\n', '- canonical glossary/speech files\n- `glossary/canonical_findings.json` directly (findings travel through the worker result and merge centrally)\n')

path = ROOT / "CONTEXT_MAINTENANCE.md"
replace_exact(path, '- `glossary/terminology_reviews.json` — explicit `lock` / `defer` / `ignore` decision ledger.\n', '- `glossary/terminology_reviews.json` — explicit `lock` / `defer` / `ignore` decision ledger.\n- `glossary/canonical_findings.json` — deduplicated systemic findings from retrospective review workers; blocking evidence, not canonical by itself.\n')
append_before(path, '## Prompt scaling and precedence', '''## Canonical findings from retrospective audit\n\nReview workers report reusable systemic defects through their own result instead of editing canonical files. The merge pipeline deduplicates them into `glossary/canonical_findings.json`. Open findings are excluded from the global 19k context hash and participate only in item-scoped invalidation. Matching decisions are deferred until the finding is resolved; unrelated reviewed entries remain reusable. Evidence growth for the same finding does not change review identity.\n\n`build_terminology_review_queue.py` ranks open findings ahead of ordinary conflicts/candidates. A maintainer verifies and lands the canonical/context rule, explicitly ignores the finding, or defers it. Matching canonical targets deterministically resolve findings on refresh; defer remains blocking. The intended loop is `audit discovery → blocking finding → canonical verification/lock → affected entries reopen → audit continues`.\n''')

path = ROOT / ".github/workflows/merge-translation-review.yml"
replace_exact(path, '      - "scripts/translation_review_common.py"\n', '      - "scripts/translation_review_common.py"\n      - "scripts/canonical_findings.py"\n')
replace_exact(path, '      - "glossary/translation_regressions.generated.json"\n', '      - "glossary/translation_regressions.generated.json"\n      - "glossary/canonical_findings.json"\n')
replace_exact(path, '            python scripts/build_translation_regression_memory.py --repo-root .\n            pytest -q\n', '            python scripts/build_translation_regression_memory.py --repo-root .\n            python scripts/canonical_findings.py --repo-root . --refresh\n            python scripts/build_terminology_review_queue.py\n            pytest -q\n')
replace_exact(path, '            git add localized_data index.json glossary/translation_regressions.generated.json work/translation_review work/parallel_state.json\n', '            git add localized_data index.json glossary/translation_regressions.generated.json glossary/canonical_findings.json glossary/terminology_review_queue.json work/translation_review work/parallel_state.json\n')

path = ROOT / ".github/workflows/sync-translation-review-plan.yml"
replace_exact(path, '      - "glossary/style_rules.json"\n', '      - "glossary/style_rules.json"\n      - "glossary/canonical_findings.json"\n')
replace_exact(path, '      - "scripts/translation_review_common.py"\n', '      - "scripts/translation_review_common.py"\n      - "scripts/canonical_findings.py"\n')
replace_exact(path, '            python scripts/harden_skill_inheritance_canon.py\n            python -m pip install -e ".[dev]"\n', '            python scripts/harden_skill_inheritance_canon.py\n            python scripts/canonical_findings.py --repo-root . --refresh\n            python -m pip install -e ".[dev]"\n')
replace_exact(path, '              glossary/translation_audit_policy.json \\\n              scripts/enforce_player_facing_canon.py \\\n', '              glossary/translation_audit_policy.json \\\n              glossary/canonical_findings.json \\\n              scripts/enforce_player_facing_canon.py \\\n')
replace_exact(path, '              scripts/harden_skill_inheritance_canon.py \\\n              scripts/translation_review_common.py \\\n', '              scripts/harden_skill_inheritance_canon.py \\\n              scripts/canonical_findings.py \\\n              scripts/translation_review_common.py \\\n')

path = ROOT / ".github/workflows/sync-context.yml"
replace_exact(path, '      - "scripts/build_terminology_review_queue.py"\n', '      - "scripts/build_terminology_review_queue.py"\n      - "scripts/canonical_findings.py"\n')
replace_exact(path, '      - "glossary/terminology_reviews.json"\n', '      - "glossary/terminology_reviews.json"\n      - "glossary/canonical_findings.json"\n')
replace_exact(path, '      - name: Build terminology review queue\n', '      - name: Refresh worker-reported canonical findings\n        run: python scripts/canonical_findings.py --repo-root . --refresh\n\n      - name: Build terminology review queue\n')
replace_exact(path, '            glossary/term_registry.json \\\n            glossary/terminology_review_queue.json \\\n', '            glossary/term_registry.json \\\n            glossary/canonical_findings.json \\\n            glossary/terminology_review_queue.json \\\n')

print("canonical finding pipeline staged")

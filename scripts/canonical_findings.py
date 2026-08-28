from __future__ import annotations

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

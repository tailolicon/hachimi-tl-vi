from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any

try:
    from scripts.ui_review_common import (
        is_review_candidate, load_json, risk_flags, risk_score,
        text_fingerprint, utc_now, visual_width, write_json,
    )
except ModuleNotFoundError:
    from ui_review_common import (  # type: ignore[no-redef]
        is_review_candidate, load_json, risk_flags, risk_score,
        text_fingerprint, utc_now, visual_width, write_json,
    )

UI_REVIEW_POLICY_VERSION = 3
_TERM_PATHS = (
    "glossary/term_registry.json",
    "glossary/ui_community_terms.json",
    "glossary/ui_short_forms.json",
)


def terminology_snapshot_hash(repo_root: Path) -> str:
    digest = hashlib.sha256()
    for rel in _TERM_PATHS:
        path = repo_root / rel
        digest.update(rel.encode("utf-8") + b"\0")
        if path.exists():
            digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def git_show_json(repo_root: Path, ref: str, path: str) -> Any:
    proc = subprocess.run(
        ["git", "-C", str(repo_root), "show", f"{ref}:{path}"],
        check=True, capture_output=True, text=True, encoding="utf-8",
    )
    return json.loads(proc.stdout)


def current_active_incomplete(repo_root: Path, terminology_hash: str) -> bool:
    active_path = repo_root / "work/ui_review/active_plan.json"
    if not active_path.exists():
        return False
    active = load_json(active_path)
    if active.get("status") != "active" or not active.get("plan_path"):
        return False
    if int(active.get("policy_version", 0)) < UI_REVIEW_POLICY_VERSION:
        return False
    if str(active.get("terminology_snapshot_sha256", "")) != terminology_hash:
        return False
    plan_path = repo_root / str(active["plan_path"])
    if not plan_path.exists():
        return False
    plan = load_json(plan_path)
    return any(
        not (repo_root / "work/ui_review/merged" / f"{batch['batch_id']}.json").exists()
        for batch in plan.get("batches", [])
    )


def source_map_from_epoch(repo_root: Path) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    state = load_json(repo_root / "work/parallel_state.json")
    epoch = load_json(repo_root / str(state["current_epoch_metadata"]))
    source_ref = str(epoch["source_queue_git_commit"])
    pattern = str(epoch["source_batch_pattern"])
    source_map: dict[str, dict[str, Any]] = {}
    for batch in range(1, int(epoch["queue_total_batches"]) + 1):
        try:
            payload = git_show_json(repo_root, source_ref, pattern.format(batch=batch))
        except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError):
            continue
        for item in payload.get("entries", []):
            if item.get("source_path") != "localize_dict.json":
                continue
            path = item.get("json_path")
            if not isinstance(path, list) or len(path) != 1:
                continue
            key = str(path[0])
            source_map[key] = {
                "source_text": str(item.get("source_text", "")),
                "source_fingerprint": str(item.get("source_fingerprint", "")),
                "source_batch": batch,
                "uid": item.get("uid"),
            }
    return source_map, epoch


def _norm(text: str) -> str:
    return " ".join(text.casefold().split())


def _load_community_terms(repo_root: Path) -> list[dict[str, Any]]:
    payload = load_json(repo_root / "glossary/ui_community_terms.json", {"terms": []})
    terms = payload.get("terms", [])
    if not isinstance(terms, list):
        raise TypeError("glossary/ui_community_terms.json terms must be a list")
    return [term for term in terms if isinstance(term, dict)]


def community_term_matches(
    key: str, source: str, target: str, terms: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    normalized_target = _norm(target)
    for term in terms:
        prefixes = [str(v) for v in term.get("key_prefixes", []) if str(v)]
        if prefixes and not any(key.startswith(prefix) for prefix in prefixes):
            continue
        aliases = [str(v) for v in term.get("source_aliases", []) if str(v)]
        if not aliases or not any(alias in source for alias in aliases):
            continue
        accepted = list(dict.fromkeys(
            [str(v) for v in term.get("accepted", []) if str(v)]
            + [str(v) for v in term.get("compact", []) if str(v)]
        ))
        forbidden = [str(v) for v in term.get("forbidden", []) if str(v)]
        result.append({
            "id": str(term.get("id", "")),
            "preferred": str(term.get("preferred", "")),
            "accepted": accepted,
            "forbidden": forbidden,
            "accepted_present": any(_norm(v) in normalized_target for v in accepted),
            "forbidden_present": any(_norm(v) in normalized_target for v in forbidden),
            "require_accepted": bool(term.get("require_accepted", True)),
            "basis": str(term.get("basis", "")),
        })
    return result


def _term_risk(matches: list[dict[str, Any]]) -> tuple[list[str], int]:
    if not matches:
        return [], 0
    flags = ["community_term"]
    score = 2
    if any(m["forbidden_present"] for m in matches):
        flags.append("community_calque_risk")
        score += 8
    if any(m["require_accepted"] and not m["accepted_present"] for m in matches):
        flags.append("community_term_mismatch")
        score += 6
    return flags, score


def build_plan(repo_root: Path, batch_size: int) -> dict[str, Any]:
    ui_root = repo_root / "work/ui_review"
    active_path = ui_root / "active_plan.json"
    terminology_hash = terminology_snapshot_hash(repo_root)
    if current_active_incomplete(repo_root, terminology_hash):
        return {"status": "active_plan_incomplete", "changed": False}

    localized = load_json(repo_root / "localized_data/localize_dict.json")
    if not isinstance(localized, dict):
        raise TypeError("localized_data/localize_dict.json must be an object")
    reviewed = load_json(ui_root / "reviewed_index.json", {"schema_version": 1, "entries": {}})
    reviewed_entries = reviewed.setdefault("entries", {})
    source_map, epoch = source_map_from_epoch(repo_root)
    community_terms = _load_community_terms(repo_root)

    candidates: list[dict[str, Any]] = []
    for raw_key, current in localized.items():
        key = str(raw_key)
        if not isinstance(current, str) or key not in source_map:
            continue
        source_item = source_map[key]
        source = str(source_item["source_text"])
        if not is_review_candidate(source, current):
            continue
        current_fp = text_fingerprint(current)
        prior = reviewed_entries.get(key)
        if (
            isinstance(prior, dict)
            and int(prior.get("policy_version", 0)) == UI_REVIEW_POLICY_VERSION
            and prior.get("current_fingerprint") == current_fp
        ):
            continue

        matches = community_term_matches(key, source, current, community_terms)
        term_flags, term_score = _term_risk(matches)
        base_flags = risk_flags(source, current)
        candidates.append({
            "key": key,
            "path": [key],
            "source_text": source,
            "source_fingerprint": source_item["source_fingerprint"],
            "source_batch": source_item["source_batch"],
            "uid": source_item.get("uid"),
            "current_text": current,
            "current_fingerprint": current_fp,
            "source_visual_width": round(visual_width(source), 2),
            "current_visual_width": round(visual_width(current), 2),
            "risk_flags": list(dict.fromkeys([*base_flags, *term_flags])),
            "risk_score": risk_score(source, current) + term_score,
            "community_terms": matches,
        })

    candidates.sort(key=lambda item: (-int(item["risk_score"]), str(item["key"])))
    localize_hash = hashlib.sha256(json.dumps(
        localized, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")).hexdigest()
    source_commit = str(epoch["source_commit"])
    plan_id = (
        f"ui-p{UI_REVIEW_POLICY_VERSION}-{source_commit[:12]}-"
        f"{localize_hash[:12]}-{terminology_hash[:10]}"
    )

    if not candidates:
        write_json(active_path, {
            "schema_version": 1,
            "status": "idle",
            "policy_version": UI_REVIEW_POLICY_VERSION,
            "plan_id": None,
            "plan_path": None,
            "generated_at": utc_now(),
            "source_commit": source_commit,
            "source_queue_git_commit": epoch["source_queue_git_commit"],
            "localize_snapshot_sha256": localize_hash,
            "terminology_snapshot_sha256": terminology_hash,
            "candidate_count": 0,
            "note": "No unchanged-unreviewed fixed-size UI candidates remain under UI review policy v3.",
        })
        return {"status": "idle", "changed": True, "candidate_count": 0}

    batch_dir = ui_root / "batches" / plan_id
    if batch_dir.exists():
        for old in batch_dir.glob("*.json"):
            old.unlink()
    batches: list[dict[str, Any]] = []
    for offset in range(0, len(candidates), batch_size):
        index = offset // batch_size + 1
        batch_id = f"{plan_id}-b{index:04d}"
        rel = Path("work/ui_review/batches") / plan_id / f"{batch_id}.json"
        items = candidates[offset:offset + batch_size]
        write_json(repo_root / rel, {
            "schema_version": 1,
            "policy_version": UI_REVIEW_POLICY_VERSION,
            "plan_id": plan_id,
            "batch_id": batch_id,
            "source_commit": source_commit,
            "source_queue_git_commit": epoch["source_queue_git_commit"],
            "terminology_snapshot_sha256": terminology_hash,
            "review_generation": "full-semantic-community-reset",
            "items": items,
        })
        batches.append({
            "batch_id": batch_id,
            "batch_path": rel.as_posix(),
            "item_count": len(items),
            "risk_score": sum(int(item["risk_score"]) for item in items),
        })

    plan_rel = Path("work/ui_review/plans") / f"{plan_id}.json"
    common = {
        "schema_version": 1,
        "policy_version": UI_REVIEW_POLICY_VERSION,
        "plan_id": plan_id,
        "generated_at": utc_now(),
        "lease_minutes": 45,
        "source_commit": source_commit,
        "source_queue_git_commit": epoch["source_queue_git_commit"],
        "localize_snapshot_sha256": localize_hash,
        "terminology_snapshot_sha256": terminology_hash,
        "candidate_count": len(candidates),
        "batch_count": len(batches),
        "review_generation": "full-semantic-community-reset",
    }
    write_json(repo_root / plan_rel, {
        **common,
        "batch_size": batch_size,
        "supersedes_policy_versions": [1, 2],
        "batches": batches,
        "decision_actions": ["keep", "revise", "defer"],
        "protocol": "UI_REVIEW.md",
    })
    write_json(active_path, {**common, "status": "active", "plan_path": plan_rel.as_posix()})
    return {
        "status": "active",
        "changed": True,
        "policy_version": UI_REVIEW_POLICY_VERSION,
        "plan_id": plan_id,
        "candidate_count": len(candidates),
        "batch_count": len(batches),
        "review_generation": "full-semantic-community-reset",
        "terminology_snapshot_sha256": terminology_hash,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a retrospective fixed-size UI review plan.")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--batch-size", type=int, default=20)
    args = parser.parse_args()
    if not 1 <= args.batch_size <= 100:
        raise SystemExit("--batch-size must be between 1 and 100")
    print(json.dumps(build_plan(args.repo_root.resolve(), args.batch_size), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

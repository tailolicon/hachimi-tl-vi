from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any

from ui_review_common import (
    is_review_candidate,
    load_json,
    risk_flags,
    risk_score,
    text_fingerprint,
    utc_now,
    visual_width,
    write_json,
)


def git_show_json(repo_root: Path, ref: str, path: str) -> Any:
    proc = subprocess.run(
        ["git", "-C", str(repo_root), "show", f"{ref}:{path}"],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return json.loads(proc.stdout)


def current_active_incomplete(repo_root: Path) -> bool:
    active_path = repo_root / "work" / "ui_review" / "active_plan.json"
    if not active_path.exists():
        return False
    active = load_json(active_path)
    if active.get("status") != "active" or not active.get("plan_path"):
        return False
    plan_path = repo_root / str(active["plan_path"])
    if not plan_path.exists():
        return False
    plan = load_json(plan_path)
    for batch in plan.get("batches", []):
        batch_id = str(batch["batch_id"])
        if not (repo_root / "work" / "ui_review" / "merged" / f"{batch_id}.json").exists():
            return True
    return False


def source_map_from_epoch(repo_root: Path) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    state = load_json(repo_root / "work" / "parallel_state.json")
    epoch = load_json(repo_root / str(state["current_epoch_metadata"]))
    source_ref = str(epoch["source_queue_git_commit"])
    pattern = str(epoch["source_batch_pattern"])
    total_batches = int(epoch["queue_total_batches"])

    source_map: dict[str, dict[str, Any]] = {}
    for batch in range(1, total_batches + 1):
        path = pattern.format(batch=batch)
        try:
            payload = git_show_json(repo_root, source_ref, path)
        except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError):
            continue
        for item in payload.get("entries", []):
            if item.get("source_path") != "localize_dict.json":
                continue
            json_path = item.get("json_path")
            if not isinstance(json_path, list) or len(json_path) != 1:
                continue
            key = str(json_path[0])
            source_map[key] = {
                "source_text": str(item.get("source_text", "")),
                "source_fingerprint": str(item.get("source_fingerprint", "")),
                "source_batch": batch,
                "uid": item.get("uid"),
            }
    return source_map, epoch


def build_plan(repo_root: Path, batch_size: int) -> dict[str, Any]:
    ui_root = repo_root / "work" / "ui_review"
    active_path = ui_root / "active_plan.json"
    if current_active_incomplete(repo_root):
        return {"status": "active_plan_incomplete", "changed": False}

    localized = load_json(repo_root / "localized_data" / "localize_dict.json")
    if not isinstance(localized, dict):
        raise TypeError("localized_data/localize_dict.json must be an object")

    reviewed = load_json(ui_root / "reviewed_index.json", {"schema_version": 1, "entries": {}})
    reviewed_entries = reviewed.setdefault("entries", {})
    source_map, epoch = source_map_from_epoch(repo_root)

    candidates: list[dict[str, Any]] = []
    for key, current in localized.items():
        if not isinstance(current, str):
            continue
        source_item = source_map.get(str(key))
        if source_item is None:
            continue
        source_text = str(source_item["source_text"])
        if not is_review_candidate(source_text, current):
            continue
        current_fp = text_fingerprint(current)
        prior = reviewed_entries.get(str(key))
        if isinstance(prior, dict) and prior.get("current_fingerprint") == current_fp:
            continue
        flags = risk_flags(source_text, current)
        candidates.append(
            {
                "key": str(key),
                "path": [str(key)],
                "source_text": source_text,
                "source_fingerprint": source_item["source_fingerprint"],
                "source_batch": source_item["source_batch"],
                "uid": source_item.get("uid"),
                "current_text": current,
                "current_fingerprint": current_fp,
                "source_visual_width": round(visual_width(source_text), 2),
                "current_visual_width": round(visual_width(current), 2),
                "risk_flags": flags,
                "risk_score": risk_score(source_text, current),
            }
        )

    candidates.sort(key=lambda item: (-int(item["risk_score"]), str(item["key"])))

    localize_hash = hashlib.sha256(
        json.dumps(localized, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    source_commit = str(epoch["source_commit"])
    plan_id = f"ui-{source_commit[:12]}-{localize_hash[:12]}"

    if not candidates:
        write_json(
            active_path,
            {
                "schema_version": 1,
                "status": "idle",
                "plan_id": None,
                "plan_path": None,
                "generated_at": utc_now(),
                "source_commit": source_commit,
                "source_queue_git_commit": epoch["source_queue_git_commit"],
                "localize_snapshot_sha256": localize_hash,
                "candidate_count": 0,
                "note": "No unchanged-unreviewed fixed-size UI candidates remain in the current translated localize snapshot.",
            },
        )
        return {"status": "idle", "changed": True, "candidate_count": 0}

    batches: list[dict[str, Any]] = []
    batch_dir = ui_root / "batches" / plan_id
    for offset in range(0, len(candidates), batch_size):
        index = offset // batch_size + 1
        batch_id = f"{plan_id}-b{index:04d}"
        items = candidates[offset : offset + batch_size]
        rel_path = Path("work") / "ui_review" / "batches" / plan_id / f"{batch_id}.json"
        write_json(
            repo_root / rel_path,
            {
                "schema_version": 1,
                "plan_id": plan_id,
                "batch_id": batch_id,
                "source_commit": source_commit,
                "source_queue_git_commit": epoch["source_queue_git_commit"],
                "items": items,
            },
        )
        batches.append(
            {
                "batch_id": batch_id,
                "batch_path": rel_path.as_posix(),
                "item_count": len(items),
                "risk_score": sum(int(item["risk_score"]) for item in items),
            }
        )

    plan_rel = Path("work") / "ui_review" / "plans" / f"{plan_id}.json"
    write_json(
        repo_root / plan_rel,
        {
            "schema_version": 1,
            "plan_id": plan_id,
            "generated_at": utc_now(),
            "lease_minutes": 45,
            "batch_size": batch_size,
            "source_commit": source_commit,
            "source_queue_git_commit": epoch["source_queue_git_commit"],
            "localize_snapshot_sha256": localize_hash,
            "candidate_count": len(candidates),
            "batch_count": len(batches),
            "batches": batches,
            "decision_actions": ["keep", "revise", "defer"],
            "protocol": "UI_REVIEW.md",
        },
    )
    write_json(
        active_path,
        {
            "schema_version": 1,
            "status": "active",
            "plan_id": plan_id,
            "plan_path": plan_rel.as_posix(),
            "generated_at": utc_now(),
            "lease_minutes": 45,
            "candidate_count": len(candidates),
            "batch_count": len(batches),
            "source_commit": source_commit,
            "source_queue_git_commit": epoch["source_queue_git_commit"],
            "localize_snapshot_sha256": localize_hash,
        },
    )
    return {
        "status": "active",
        "changed": True,
        "plan_id": plan_id,
        "candidate_count": len(candidates),
        "batch_count": len(batches),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a retrospective fixed-size UI review plan.")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--batch-size", type=int, default=20)
    args = parser.parse_args()
    if args.batch_size < 1 or args.batch_size > 100:
        raise SystemExit("--batch-size must be between 1 and 100")
    report = build_plan(args.repo_root.resolve(), args.batch_size)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

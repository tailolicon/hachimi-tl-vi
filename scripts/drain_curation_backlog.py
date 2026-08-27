from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

import merge_parallel_curation as core

FAILURE_ROOT = core.WORK_ROOT / "merge_failures"


def matching_completion(batch_id: str, claim_id: str, plan_id: str) -> tuple[Path, dict[str, Any]] | None:
    completion_dir = core.WORK_ROOT / "completions" / batch_id
    if not completion_dir.exists():
        return None
    for path in sorted(completion_dir.glob("*.json")):
        doc = core.read_json(path, {}) or {}
        if not isinstance(doc, dict):
            continue
        if str(doc.get("plan_id") or "") != plan_id:
            continue
        if str(doc.get("batch_id") or "") != batch_id:
            continue
        if str(doc.get("claim_id") or "") != claim_id:
            continue
        return path, doc
    return None


def same_failure(path: Path, *, plan_id: str, batch_id: str, claim_id: str, result_path: Path) -> bool:
    doc = core.read_json(path, {}) or {}
    if not isinstance(doc, dict):
        return False
    return (
        str(doc.get("plan_id") or "") == plan_id
        and str(doc.get("batch_id") or "") == batch_id
        and str(doc.get("claim_id") or "") == claim_id
        and str(doc.get("result_path") or "") == result_path.relative_to(core.ROOT).as_posix()
    )


def record_failure(
    path: Path,
    *,
    plan_id: str,
    batch_id: str,
    claim_id: str,
    worker_id: str,
    completion_path: Path,
    result_path: Path,
    error: Exception,
) -> None:
    core.write_json(
        path,
        {
            "schema_version": 1,
            "plan_id": plan_id,
            "batch_id": batch_id,
            "claim_id": claim_id,
            "worker_id": worker_id,
            "failed_at": core.utc_now(),
            "completion_path": completion_path.relative_to(core.ROOT).as_posix(),
            "result_path": result_path.relative_to(core.ROOT).as_posix(),
            "error": str(error)[:4000],
        },
    )


def drain(*, active_path: Path = core.DEFAULT_ACTIVE, max_batches: int | None = None) -> dict[str, int]:
    active, plan, _ = core.load_active_plan(active_path)
    plan_id = str(active["plan_id"])
    batches = core.batch_index(plan)
    speech_bible = core.read_json(core.DEFAULT_SPEECH_BIBLE, {}) or {}
    reviews = core.read_json(core.DEFAULT_TERM_REVIEWS, {}) or {}
    if not isinstance(speech_bible, dict) or not isinstance(reviews, dict):
        raise ValueError("canonical curation files must be JSON objects")

    stats = {
        "batches": 0,
        "speech_profiles": 0,
        "terminology_decisions": 0,
        "failed_batches": 0,
        "previous_failures_skipped": 0,
        "not_ready": 0,
    }

    for batch_id, batch in sorted(batches.items()):
        merged_path = core.WORK_ROOT / "merged" / f"{batch_id}.json"
        if merged_path.exists():
            continue

        claim_path = core.WORK_ROOT / "claims" / f"{batch_id}.json"
        claim = core.read_json(claim_path, {}) or {}
        if not isinstance(claim, dict):
            stats["not_ready"] += 1
            continue
        if str(claim.get("plan_id") or "") != plan_id or str(claim.get("batch_id") or "") != batch_id:
            stats["not_ready"] += 1
            continue
        claim_id = str(claim.get("claim_id") or "").strip()
        if not claim_id:
            stats["not_ready"] += 1
            continue

        matched = matching_completion(batch_id, claim_id, plan_id)
        if matched is None:
            stats["not_ready"] += 1
            continue
        completion_path, completion = matched

        result_path = core.WORK_ROOT / "results" / batch_id / f"{claim_id}.json"
        result = core.read_json(result_path, {}) or {}
        if not isinstance(result, dict):
            result = {}

        failure_path = FAILURE_ROOT / f"{batch_id}.json"
        if same_failure(
            failure_path,
            plan_id=plan_id,
            batch_id=batch_id,
            claim_id=claim_id,
            result_path=result_path,
        ):
            stats["previous_failures_skipped"] += 1
            continue

        worker_id = str(claim.get("worker_id") or (result.get("worker_id") if isinstance(result, dict) else "") or "unknown")
        try:
            if not isinstance(result, dict) or not result:
                raise ValueError(f"{batch_id}: missing result for completion {completion_path}")
            core.validate_envelope(result, completion, claim, plan_id=plan_id, batch_id=batch_id)
            kind = str(batch.get("kind") or "")
            if kind == "speech":
                candidate = copy.deepcopy(speech_bible)
                added = core.merge_speech_batch(
                    batch,
                    result,
                    candidate,
                    plan_id=plan_id,
                    batch_id=batch_id,
                    claim_id=claim_id,
                    worker_id=worker_id,
                )
                speech_bible = candidate
                stats["speech_profiles"] += added
            elif kind == "terminology":
                candidate = copy.deepcopy(reviews)
                added = core.merge_term_batch(
                    batch,
                    result,
                    candidate,
                    plan_id=plan_id,
                    batch_id=batch_id,
                    claim_id=claim_id,
                    worker_id=worker_id,
                )
                reviews = candidate
                stats["terminology_decisions"] += added
            else:
                raise ValueError(f"{batch_id}: unsupported curation batch kind {kind!r}")
        except (ValueError, TypeError, KeyError) as exc:
            record_failure(
                failure_path,
                plan_id=plan_id,
                batch_id=batch_id,
                claim_id=claim_id,
                worker_id=worker_id,
                completion_path=completion_path,
                result_path=result_path,
                error=exc,
            )
            stats["failed_batches"] += 1
            continue

        core.write_json(
            merged_path,
            {
                "schema_version": 1,
                "plan_id": plan_id,
                "batch_id": batch_id,
                "claim_id": claim_id,
                "worker_id": worker_id,
                "merged_at": core.utc_now(),
                "result_path": result_path.relative_to(core.ROOT).as_posix(),
            },
        )
        if failure_path.exists():
            failure_path.unlink()
        stats["batches"] += 1
        if max_batches is not None and stats["batches"] >= max_batches:
            break

    if stats["batches"]:
        core.write_json(core.DEFAULT_SPEECH_BIBLE, speech_bible)
        core.write_json(core.DEFAULT_TERM_REVIEWS, reviews)
    return stats


def main() -> int:
    parser = argparse.ArgumentParser(description="Drain valid curation batches while isolating invalid ones.")
    parser.add_argument("--active", type=Path, default=core.DEFAULT_ACTIVE)
    parser.add_argument("--max-batches", type=int, default=50)
    args = parser.parse_args()
    try:
        stats = drain(active_path=args.active, max_batches=args.max_batches)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    print(json.dumps(stats, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

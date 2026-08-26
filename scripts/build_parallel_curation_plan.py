from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SPEECH_QUEUE = ROOT / "glossary/speech_review_queue.json"
DEFAULT_TERM_QUEUE = ROOT / "glossary/terminology_review_queue.json"
DEFAULT_ACTIVE = ROOT / "work/curation/active_plan.json"
DEFAULT_PLANS = ROOT / "work/curation/plans"

SPEECH_BATCH_SIZE = 5
TERM_BATCH_SIZE = 20


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return default
    return json.loads(text)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def source_commit_of(*docs: dict[str, Any]) -> str:
    values = {str(doc.get("source_commit") or "").strip() for doc in docs}
    values.discard("")
    if len(values) != 1:
        raise ValueError(f"curation queues must agree on one source_commit, got {sorted(values)!r}")
    return next(iter(values))


def speech_tasks(queue: dict[str, Any]) -> list[dict[str, Any]]:
    tasks: list[dict[str, Any]] = []
    for row in queue.get("characters", []):
        if not isinstance(row, dict) or row.get("status") != "needs_curated_review":
            continue
        key = str(row.get("character_key") or "").strip()
        canonical = str(row.get("canonical") or "").strip()
        if not key or not canonical:
            continue
        tasks.append(
            {
                "character_key": key,
                "canonical": canonical,
                "game_id": row.get("game_id"),
                "priority": int(row.get("priority", 0) or 0),
                "dialogue_count": int(row.get("dialogue_count", 0) or 0),
                "sample_count": int(row.get("sample_count", 0) or 0),
                "source_speakers": row.get("source_speakers", []),
            }
        )
    return tasks


def term_tasks(queue: dict[str, Any]) -> list[dict[str, Any]]:
    tasks: list[dict[str, Any]] = []
    for row in queue.get("review_queue", []):
        if not isinstance(row, dict):
            continue
        status = str(row.get("status") or "").strip()
        if status in {"canonical_locked", "handled_by_character_registry", "resolved", "covered"}:
            continue
        source = str(row.get("source_zh_cn") or "").strip()
        if not source:
            continue
        locators = row.get("locators", [])
        if not isinstance(locators, list):
            locators = []
        tasks.append(
            {
                "source_zh_cn": source,
                "kinds": row.get("kinds", []),
                "primary_kind": row.get("primary_kind"),
                "status": status,
                "priority": int(row.get("priority", 0) or 0),
                "reason": row.get("reason"),
                "locators": locators[:3],
            }
        )
    return tasks


def _max_batch_no(batches: list[dict[str, Any]], prefix: str) -> int:
    value = 0
    for batch in batches:
        batch_id = str(batch.get("batch_id") or "")
        if not batch_id.startswith(prefix + "-"):
            continue
        try:
            value = max(value, int(batch_id.rsplit("-", 1)[1]))
        except ValueError:
            pass
    return value


def _chunk_new(
    existing: list[dict[str, Any]],
    tasks: list[dict[str, Any]],
    *,
    prefix: str,
    identity_field: str,
    batch_size: int,
) -> tuple[list[dict[str, Any]], int]:
    seen: set[str] = set()
    for batch in existing:
        for item in batch.get("items", []):
            if isinstance(item, dict):
                identity = str(item.get(identity_field) or "").strip()
                if identity:
                    seen.add(identity)

    pending = [task for task in tasks if str(task.get(identity_field) or "").strip() not in seen]
    if not pending:
        return existing, 0

    next_no = _max_batch_no(existing, prefix) + 1
    added = 0
    out = list(existing)
    for offset in range(0, len(pending), batch_size):
        chunk = pending[offset : offset + batch_size]
        out.append(
            {
                "batch_id": f"{prefix}-{next_no:04d}",
                "kind": "speech" if prefix == "speech" else "terminology",
                "items": chunk,
            }
        )
        next_no += 1
        added += 1
    return out, added


def build_or_extend_plan(
    speech_queue: dict[str, Any],
    term_queue: dict[str, Any],
    existing: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], dict[str, int]]:
    source_commit = source_commit_of(speech_queue, term_queue)
    plan_id = f"ctx-{source_commit[:16]}-v1"
    existing = existing if isinstance(existing, dict) and existing.get("plan_id") == plan_id else None

    if existing:
        plan = dict(existing)
        speech_batches = list(plan.get("speech_batches", []))
        term_batches = list(plan.get("terminology_batches", []))
    else:
        plan = {
            "schema_version": 1,
            "plan_id": plan_id,
            "source_commit": source_commit,
            "created_at": utc_now(),
            "lease_minutes": 45,
            "speech_batch_size": SPEECH_BATCH_SIZE,
            "terminology_batch_size": TERM_BATCH_SIZE,
            "policy": {
                "canonical_writes": "Workers never edit glossary canonical files. They only claim a batch and write claim-scoped result/completion files.",
                "speech_precedence": "Source scene > reviewed curated speech profile > evidence fallback.",
                "terminology_safety": "A terminology lock is merged only through terminology_reviews.json and apply_terminology_reviews.py validation.",
            },
            "speech_batches": [],
            "terminology_batches": [],
        }
        speech_batches = []
        term_batches = []

    speech_batches, added_speech = _chunk_new(
        speech_batches,
        speech_tasks(speech_queue),
        prefix="speech",
        identity_field="character_key",
        batch_size=SPEECH_BATCH_SIZE,
    )
    term_batches, added_terms = _chunk_new(
        term_batches,
        term_tasks(term_queue),
        prefix="term",
        identity_field="source_zh_cn",
        batch_size=TERM_BATCH_SIZE,
    )
    plan["speech_batches"] = speech_batches
    plan["terminology_batches"] = term_batches
    if added_speech or added_terms:
        plan["updated_at"] = utc_now()
    plan["summary"] = {
        "speech_batches": len(speech_batches),
        "speech_items": sum(len(batch.get("items", [])) for batch in speech_batches),
        "terminology_batches": len(term_batches),
        "terminology_items": sum(len(batch.get("items", [])) for batch in term_batches),
    }
    return plan, {"speech_batches_added": added_speech, "terminology_batches_added": added_terms}


def main() -> int:
    parser = argparse.ArgumentParser(description="Build or extend an immutable-ID parallel curation plan.")
    parser.add_argument("--speech-queue", type=Path, default=DEFAULT_SPEECH_QUEUE)
    parser.add_argument("--term-queue", type=Path, default=DEFAULT_TERM_QUEUE)
    parser.add_argument("--active", type=Path, default=DEFAULT_ACTIVE)
    parser.add_argument("--plans-dir", type=Path, default=DEFAULT_PLANS)
    args = parser.parse_args()

    speech_queue = read_json(args.speech_queue, {}) or {}
    term_queue = read_json(args.term_queue, {}) or {}
    if not isinstance(speech_queue, dict) or not isinstance(term_queue, dict):
        raise SystemExit("curation queues must be JSON objects")

    source_commit = source_commit_of(speech_queue, term_queue)
    plan_id = f"ctx-{source_commit[:16]}-v1"
    plan_path = args.plans_dir / f"{plan_id}.json"
    existing = read_json(plan_path, None)
    plan, stats = build_or_extend_plan(speech_queue, term_queue, existing)

    args.plans_dir.mkdir(parents=True, exist_ok=True)
    plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.active.parent.mkdir(parents=True, exist_ok=True)
    active = {
        "schema_version": 1,
        "plan_id": plan_id,
        "source_commit": source_commit,
        "plan_path": plan_path.relative_to(ROOT).as_posix(),
        "lease_minutes": int(plan.get("lease_minutes", 45)),
    }
    args.active.write_text(json.dumps(active, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({**plan["summary"], **stats}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

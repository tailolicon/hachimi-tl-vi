#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

START = "<!-- AUTO_PROGRESS_START -->"
END = "<!-- AUTO_PROGRESS_END -->"


def load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        value = json.load(fh)
    if not isinstance(value, dict):
        raise SystemExit(f"Expected JSON object: {path}")
    return value


def pct(done: int, total: int) -> float:
    return 0.0 if total <= 0 else (done * 100.0 / total)


def roadmap_label(state: dict[str, Any]) -> str:
    rows = []
    for item in state.get("roadmap") or []:
        if not isinstance(item, dict):
            continue
        status = str(item.get("status") or "")
        if status not in {"active", "pending", "ready_for_integration"}:
            continue
        title = str(item.get("title") or item.get("id") or "unknown")
        marker = "▶" if status == "active" else ("✓→" if status == "ready_for_integration" else "→")
        suffix = " [ready for integration]" if status == "ready_for_integration" else ""
        rows.append(f"{marker} {title}{suffix}")
        if len(rows) >= 6:
            break
    return "<br>".join(rows) if rows else "No pending roadmap item"


def maintenance_stage(active: dict[str, Any]) -> str:
    stage = str(active.get("stage") or "").strip()
    if stage:
        return stage
    if str(active.get("status") or "") == "complete":
        return "complete"
    return "domain_work"


def canonical_parallel_summary(state: dict[str, Any]) -> str:
    cfg = state.get("canonical_parallelism") or {}
    if not cfg.get("enabled"):
        return "disabled / legacy serial mode"

    pending = 0
    ready = 0
    complete = 0
    for item in state.get("roadmap") or []:
        if not isinstance(item, dict) or item.get("kind") != "canonical_hardening":
            continue
        status = str(item.get("status") or "")
        if status == "ready_for_integration":
            ready += 1
        elif status == "complete":
            complete += 1
        elif item.get("parallel_eligible") is True and status in {"pending", "active"}:
            pending += 1

    limit = int(cfg.get("max_parallel_domain_workers") or 0)
    return (
        f"**ON** — domain work parallel / integration serial; "
        f"{pending} active-or-claimable domain lanes, {ready} ready for integration, {complete} canonical domains complete"
        + (f"; configured domain-worker cap {limit}" if limit else "")
    )


def build_block(progress: dict[str, Any], state: dict[str, Any]) -> str:
    t = progress.get("translation") or {}
    r = progress.get("translation_review") or {}
    u = progress.get("ui_review") or {}
    c = progress.get("curation") or {}
    workers = progress.get("workers") or {}
    active = state.get("active_task") or {}

    total = int(t.get("source_total_entries") or 0)
    translated = int(t.get("translated_entries") or 0)
    remaining_total = max(total - translated, 0)
    queued = int(t.get("queued_entries") or 0)
    remaining_queue = int(t.get("remaining_queue_entries") or max(queued - translated, 0))
    deferred = int(t.get("deferred_entries") or 0)

    review_candidates = int(r.get("candidates") or 0)
    review_resolved = int(r.get("resolved_entries") or 0)
    ui_candidates = int(u.get("candidates") or 0)
    ui_done = int(u.get("reviewed_items") or 0)
    gate = "LOCKED" if bool(r.get("gate_enabled")) else "OPEN"

    speech = c.get("speech") or {}
    terminology = c.get("terminology") or {}

    phase = str(state.get("phase") or "unknown")
    task_title = str(active.get("title") or active.get("task_id") or "none")
    task_branch = str(active.get("branch") or "main")
    task_stage = maintenance_stage(active)
    spawn = str(state.get("short_spawn_prompt") or "Run tailolicon/hachimi-tl-vi/WORKER_START.md from main.")

    return "\n".join(
        [
            START,
            "## Live project control",
            "",
            f"**Spawn worker (the only prompt you need):** `{spawn}`",
            "",
            "| Metric | Live state |",
            "| --- | --- |",
            f"| Current phase | **{phase}** |",
            f"| Primary integration lane | **{task_title}** — stage **{task_stage}** (`{task_branch}`) |",
            f"| Canonical parallelism | {canonical_parallel_summary(state)} |",
            f"| Pinned source coverage | **{translated:,} / {total:,} ({pct(translated, total):.2f}%)** — {remaining_total:,} remaining |",
            f"| Current translation wave | **{translated:,} / {queued:,} ({pct(translated, queued):.2f}%)** — {remaining_queue:,} queued remaining |",
            f"| Deferred pinned entries | **{deferred:,}** — these must be promoted in later deterministic waves, not ignored |",
            f"| Translation Audit Round 1 | **{review_resolved:,} / {review_candidates:,} resolved ({pct(review_resolved, review_candidates):.2f}%)** — gate **{gate}** |",
            f"| UI review | **{ui_done:,} / {ui_candidates:,} reviewed items ({pct(ui_done, ui_candidates):.2f}%)** |",
            f"| Context curation | Speech **{float(speech.get('merged_percent') or 0):.2f}%**, terminology **{float(terminology.get('merged_percent') or 0):.2f}%** |",
            f"| Active worker claims | **{int(workers.get('active_total') or 0)}** |",
            "",
            "**Roadmap:** " + roadmap_label(state),
            "",
            "Machine routing lives in `work/orchestration/state.json`; canonical parallel rules are in `CANONICAL_PARALLEL.md`; detailed lifecycle is in `AUTOPILOT.md`. This block is generated from canonical repository state. The `status` branch keeps the timestamped detailed progress snapshot.",
            END,
        ]
    )


def replace_block(readme: str, block: str) -> str:
    if START in readme and END in readme:
        before, rest = readme.split(START, 1)
        _, after = rest.split(END, 1)
        return before.rstrip() + "\n\n" + block + "\n\n" + after.lstrip()

    lines = readme.splitlines()
    if not lines:
        return block + "\n"

    insert_at = min(len(lines), 1)
    while insert_at < len(lines) and not lines[insert_at].strip():
        insert_at += 1
    while insert_at < len(lines) and lines[insert_at].strip():
        insert_at += 1
    head = "\n".join(lines[:insert_at]).rstrip()
    tail = "\n".join(lines[insert_at:]).lstrip()
    if tail:
        return head + "\n\n" + block + "\n\n" + tail + "\n"
    return head + "\n\n" + block + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    ap.add_argument("--progress-json", type=Path, required=True)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    root = args.repo_root.resolve()
    readme_path = root / "README.md"
    state_path = root / "work/orchestration/state.json"
    progress = load(args.progress_json.resolve())
    state = load(state_path)
    old = readme_path.read_text(encoding="utf-8")
    new = replace_block(old, build_block(progress, state))

    if args.check:
        if new != old:
            print("README live progress block is stale")
            return 1
        print("README live progress block is current")
        return 0

    if new != old:
        readme_path.write_text(new, encoding="utf-8", newline="\n")
        print("README live progress block updated")
    else:
        print("README live progress block unchanged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

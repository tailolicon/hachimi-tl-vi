from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
from typing import Any

from hachimi_tl_vi.parallel import set_json_path, structural_qa, task_id, task_slice
from hachimi_tl_vi.translation_guard import TranslationQualityGuard


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def git_show_json(repo_root: Path, ref: str, path: str) -> Any:
    proc = subprocess.run(
        ["git", "-C", str(repo_root), "show", f"{ref}:{path}"],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return json.loads(proc.stdout)


def _entry_key(source: dict[str, Any]) -> str | None:
    path = source.get("json_path")
    if isinstance(path, list) and path:
        first = path[0]
        if isinstance(first, str):
            return first
    return None


def validate_result(
    *,
    epoch: dict[str, Any],
    marker: dict[str, Any],
    result: dict[str, Any],
    source_batch: dict[str, Any],
    quality_guard: TranslationQualityGuard | None = None,
) -> tuple[list[dict[str, Any]], list[str]]:
    errors: list[str] = []
    batch = int(result.get("batch", -1))
    shard = int(result.get("shard", -1))
    expected_task_id = task_id(batch, shard)

    for obj_name, obj in (("marker", marker), ("result", result)):
        if obj.get("epoch") != epoch["epoch"]:
            errors.append(f"{obj_name}: epoch mismatch")
        if obj.get("task_id") != expected_task_id:
            errors.append(f"{obj_name}: task_id mismatch")
        if obj.get("source_commit") != epoch["source_commit"]:
            errors.append(f"{obj_name}: source_commit mismatch")
        if obj.get("source_queue_git_commit") != epoch["source_queue_git_commit"]:
            errors.append(f"{obj_name}: source_queue_git_commit mismatch")

    if marker.get("qa_passed") is not True:
        errors.append("marker: qa_passed is not true")
    if result.get("status") != "complete":
        errors.append("result: status is not complete")
    if int(source_batch.get("batch", -1)) != batch:
        errors.append("source batch number mismatch")
    if source_batch.get("source_commit") != epoch["source_commit"]:
        errors.append("source batch upstream commit mismatch")

    source_entries = source_batch.get("entries")
    if not isinstance(source_entries, list):
        errors.append("source batch entries missing")
        return [], errors

    start, end = task_slice(len(source_entries), shard, int(epoch["task_size"]))
    if start >= len(source_entries):
        errors.append("shard does not exist in source batch")
        return [], errors
    if int(result.get("shard_start", -1)) != start or int(result.get("shard_end_exclusive", -1)) != end:
        errors.append("result shard bounds mismatch")

    result_entries = result.get("entries")
    if not isinstance(result_entries, list):
        errors.append("result entries missing")
        return [], errors
    if len(result_entries) != end - start:
        errors.append(f"result entry count {len(result_entries)} != expected {end - start}")

    by_index: dict[int, dict[str, Any]] = {}
    for item in result_entries:
        try:
            idx = int(item["entry_index"])
        except (KeyError, TypeError, ValueError):
            errors.append("result contains entry without valid entry_index")
            continue
        if idx in by_index:
            errors.append(f"duplicate entry_index {idx}")
        by_index[idx] = item

    operations: list[dict[str, Any]] = []
    for idx in range(start, end):
        source = source_entries[idx]
        item = by_index.get(idx)
        if item is None:
            errors.append(f"missing entry_index {idx}")
            continue

        for field in ("uid", "kind", "source_text", "source_fingerprint", "source_path", "json_path"):
            if item.get(field) != source.get(field):
                errors.append(f"entry {idx}: {field} mismatch")

        target = item.get("target_text")
        if not isinstance(target, str) or not target.strip():
            errors.append(f"entry {idx}: target_text is empty")
            continue
        if item.get("reviewed") is not True:
            errors.append(f"entry {idx}: reviewed is not true")

        source_text = str(source.get("source_text", ""))
        qa = structural_qa(source_text, target)
        if not qa["passed"]:
            errors.append(f"entry {idx}: structural QA failed: {', '.join(qa['errors'])}")

        if quality_guard is not None:
            guard_errors = quality_guard.validate(
                source_text,
                target,
                uid=str(source.get("uid", "")) or None,
                key=_entry_key(source),
                source_path=str(source.get("source_path", "")) or None,
                json_path=source.get("json_path") if isinstance(source.get("json_path"), list) else None,
            )
            if guard_errors:
                errors.append(
                    f"entry {idx}: persistent quality guard failed: {', '.join(guard_errors)}"
                )

        operations.append(
            {
                "source_path": source["source_path"],
                "json_path": source["json_path"],
                "target_text": target,
                "entry_index": idx,
            }
        )

    expected_count = end - start
    marker_entry_count = marker.get("entry_count")
    marker_translated_count = marker.get("translated_count")
    if marker_entry_count is None:
        # Older parallel workers used translated_count on completion markers.
        # Keep those durable completions aggregatable instead of stranding valid
        # work solely because the protocol did not name entry_count explicitly.
        marker_entry_count = marker_translated_count
    elif marker_translated_count is not None:
        try:
            if int(marker_entry_count) != int(marker_translated_count):
                errors.append("marker count fields disagree")
        except (TypeError, ValueError):
            errors.append("marker count fields invalid")

    try:
        if int(marker_entry_count) != expected_count:
            errors.append("marker entry_count mismatch")
    except (TypeError, ValueError):
        errors.append("marker entry_count mismatch")
    if int(result.get("translated_count", -1)) != expected_count:
        errors.append("result translated_count mismatch")

    return operations, errors


def aggregate(repo_root: Path) -> dict[str, Any]:
    parallel_root = repo_root / "work" / "parallel"
    localized_root = repo_root / "localized_data"
    quality_guard = TranslationQualityGuard(repo_root / "glossary")
    report: dict[str, Any] = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "aggregated_tasks": [],
        "skipped_already_aggregated": [],
        "pending_tasks": [],
        "invalid_tasks": [],
        "aggregated_entries": 0,
    }
    docs: dict[Path, Any] = {}
    dirty_docs: set[Path] = set()

    if not parallel_root.exists():
        write_json(repo_root / "work" / "aggregation_report.json", report)
        return report

    markers = sorted(parallel_root.glob("*/completed/**/*.json"))
    for marker_path in markers:
        epoch_dir = marker_path.parents[2]
        epoch_path = epoch_dir / "epoch.json"
        if not epoch_path.exists():
            report["invalid_tasks"].append({"marker": str(marker_path.relative_to(repo_root)), "errors": ["epoch metadata missing"]})
            continue
        epoch = load_json(epoch_path)
        group = marker_path.parent.name
        filename = marker_path.name
        aggregated_path = epoch_dir / "aggregated" / group / filename
        if aggregated_path.exists():
            report["skipped_already_aggregated"].append(filename.removesuffix(".json"))
            continue

        marker = load_json(marker_path)
        result_path = epoch_dir / "results" / group / filename
        if not result_path.exists():
            report["invalid_tasks"].append({"task_id": marker.get("task_id"), "errors": ["result file missing"]})
            continue
        result = load_json(result_path)

        try:
            batch = int(result["batch"])
            source_batch_path = epoch["source_batch_pattern"].format(batch=batch)
            source_batch = git_show_json(repo_root, epoch["source_queue_git_commit"], source_batch_path)
        except Exception as exc:  # noqa: BLE001 - report and leave task untouched
            report["invalid_tasks"].append({"task_id": marker.get("task_id"), "errors": [f"cannot load pinned source batch: {exc}"]})
            continue

        operations, errors = validate_result(
            epoch=epoch,
            marker=marker,
            result=result,
            source_batch=source_batch,
            quality_guard=quality_guard,
        )
        if errors:
            report["invalid_tasks"].append({"task_id": marker.get("task_id"), "errors": errors})
            continue

        blocked: list[str] = []
        task_docs: dict[Path, Any] = {}
        for op in operations:
            target_path = localized_root / op["source_path"]
            if target_path not in docs and target_path not in task_docs:
                if target_path.exists():
                    task_docs[target_path] = load_json(target_path)
                elif str(op["source_path"]).startswith("assets/"):
                    blocked.append(f"source template not present for {op['source_path']}")
                else:
                    task_docs[target_path] = {}
        if blocked:
            report["pending_tasks"].append({"task_id": marker.get("task_id"), "reasons": sorted(set(blocked))})
            continue

        for path, document in task_docs.items():
            docs.setdefault(path, document)
        for op in operations:
            target_path = localized_root / op["source_path"]
            set_json_path(docs[target_path], op["json_path"], op["target_text"])
            dirty_docs.add(target_path)

        write_json(
            aggregated_path,
            {
                "schema_version": 1,
                "epoch": epoch["epoch"],
                "task_id": marker["task_id"],
                "source_commit": epoch["source_commit"],
                "source_queue_git_commit": epoch["source_queue_git_commit"],
                "entry_count": len(operations),
                "aggregated_at": datetime.now(timezone.utc).isoformat(),
            },
        )
        report["aggregated_tasks"].append(marker["task_id"])
        report["aggregated_entries"] += len(operations)

    for path in sorted(dirty_docs):
        write_json(path, docs[path])

    report["summary"] = {
        "completed_markers_seen": len(markers),
        "new_tasks_aggregated": len(report["aggregated_tasks"]),
        "already_aggregated": len(report["skipped_already_aggregated"]),
        "pending": len(report["pending_tasks"]),
        "invalid": len(report["invalid_tasks"]),
    }
    write_json(repo_root / "work" / "aggregation_report.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and aggregate completed parallel translation shards.")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    args = parser.parse_args()
    report = aggregate(args.repo_root.resolve())
    print(json.dumps(report.get("summary", report), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

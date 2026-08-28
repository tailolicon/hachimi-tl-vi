from __future__ import annotations

import argparse
import json
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Any

from hachimi_tl_vi.qa import qa_pair
from hachimi_tl_vi.translation_guard import TranslationQualityGuard


def _git_show(ref: str, path: str) -> str:
    proc = subprocess.run(
        ["git", "show", f"{ref}:{path}"],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return proc.stdout


def _load_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _set_path(doc: Any, path: list[Any], value: str) -> None:
    if not path:
        raise ValueError("empty json_path is not supported")
    node = doc
    for index, segment in enumerate(path[:-1]):
        next_segment = path[index + 1]
        if isinstance(node, dict):
            if segment not in node:
                node[segment] = [] if isinstance(next_segment, int) else {}
            node = node[segment]
        elif isinstance(node, list):
            if not isinstance(segment, int):
                raise TypeError(f"list path segment must be int, got {segment!r}")
            while len(node) <= segment:
                node.append(None)
            if node[segment] is None:
                node[segment] = [] if isinstance(next_segment, int) else {}
            node = node[segment]
        else:
            raise TypeError(f"cannot descend into {type(node).__name__}")

    last = path[-1]
    if isinstance(node, dict):
        node[last] = value
    elif isinstance(node, list):
        if not isinstance(last, int):
            raise TypeError(f"list path segment must be int, got {last!r}")
        while len(node) <= last:
            node.append(None)
        node[last] = value
    else:
        raise TypeError(f"cannot assign into {type(node).__name__}")


def _recover_runtime_newlines(source: str, target: str) -> str | None:
    """Recover the legacy worker bug that decoded literal ``\\n`` into real newlines."""
    if source.count("\n") != 0:
        return None

    source_runtime = source.count("\\n")
    target_runtime = target.count("\\n")
    target_real = target.count("\n")
    if target_real == 0:
        return None
    if target_runtime + target_real != source_runtime:
        return None

    recovered = target.replace("\n", "\\n")
    if recovered.count("\\n") != source_runtime or recovered.count("\n") != 0:
        return None
    return recovered


def _collect_results(results_root: Path) -> dict[int, list[dict[str, Any]]]:
    by_batch: dict[int, list[dict[str, Any]]] = defaultdict(list)
    if not results_root.exists():
        return by_batch
    for part in sorted(results_root.glob("batch-*/*/part-*.json")):
        payload = _load_json(part)
        if not isinstance(payload, dict):
            continue
        batch = payload.get("batch")
        if isinstance(batch, int):
            payload["_result_path"] = part.as_posix()
            by_batch[batch].append(payload)
    return by_batch


def _source_batch(source_ref: str, batch: int) -> dict[str, Any]:
    path = f"work/source_batches/batch-{batch:05d}.json"
    return json.loads(_git_show(source_ref, path))


def _entry_key(source_entry: dict[str, Any]) -> str | None:
    path = source_entry.get("json_path")
    if isinstance(path, list) and path and isinstance(path[0], str):
        return path[0]
    return None


def _validate_and_complete(
    source: dict[str, Any],
    source_ref: str,
    result_payloads: list[dict[str, Any]],
    quality_guard: TranslationQualityGuard | None = None,
) -> tuple[dict[str, str] | None, list[str], set[str]]:
    diagnostics: list[str] = []
    blocking_errors: list[str] = []
    source_commit = source.get("source_commit")
    source_entries = source.get("entries", [])
    source_by_uid = {e["uid"]: e for e in source_entries if isinstance(e, dict) and "uid" in e}
    candidates: dict[str, set[str]] = defaultdict(set)
    claims: set[str] = set()

    for payload in result_payloads:
        result_path = payload.get("_result_path")
        claim_id = str(payload.get("claim_id", "unknown"))
        if payload.get("source_commit") != source_commit:
            diagnostics.append(f"{result_path}:ignored_source_commit_mismatch")
            continue
        if payload.get("source_batch_ref") != source_ref:
            diagnostics.append(f"{result_path}:ignored_source_ref_mismatch")
            continue

        claims.add(claim_id)
        for item in payload.get("translations", []):
            if not isinstance(item, dict):
                diagnostics.append(f"{result_path}:ignored_non_object_translation")
                continue
            uid = item.get("uid")
            target = item.get("target_text")
            fingerprint = item.get("source_fingerprint")
            if uid not in source_by_uid or not isinstance(target, str):
                diagnostics.append(f"{result_path}:ignored_unknown_or_invalid_uid:{uid}")
                continue
            source_entry = source_by_uid[uid]
            if fingerprint != source_entry.get("source_fingerprint"):
                diagnostics.append(f"{result_path}:ignored_fingerprint_mismatch:{uid}")
                continue

            source_text = source_entry.get("source_text", "")
            qa = qa_pair(source_text, target)
            if qa["problems"] == ["newline_count_changed"]:
                recovered = _recover_runtime_newlines(source_text, target)
                if recovered is not None:
                    recovered_qa = qa_pair(source_text, recovered)
                    if not recovered_qa["problems"]:
                        target = recovered
                        qa = recovered_qa
                        diagnostics.append(f"{result_path}:recovered_runtime_newline:{uid}")

            if qa["problems"]:
                diagnostics.append(
                    f"{result_path}:ignored_qa:{uid}:{','.join(qa['problems'])}"
                )
                continue

            if quality_guard is not None:
                guard_errors = quality_guard.validate(
                    str(source_text),
                    target,
                    uid=str(uid),
                    key=_entry_key(source_entry),
                    source_path=str(source_entry.get("source_path", "")) or None,
                    json_path=source_entry.get("json_path") if isinstance(source_entry.get("json_path"), list) else None,
                )
                if guard_errors:
                    diagnostics.append(
                        f"{result_path}:ignored_quality_guard:{uid}:{','.join(guard_errors)}"
                    )
                    continue
            candidates[uid].add(target)

    resolved: dict[str, str] = {}
    missing: list[str] = []
    for uid in source_by_uid:
        values = candidates.get(uid, set())
        if not values:
            missing.append(uid)
            continue
        if len(values) > 1:
            blocking_errors.append(f"translation_conflict:{uid}")
            continue
        resolved[uid] = next(iter(values))

    if missing:
        diagnostics.append(f"missing_uids:{len(missing)}")
    diagnostics.extend(blocking_errors)

    if missing or blocking_errors:
        return None, diagnostics, claims
    return resolved, diagnostics, claims


def _apply_batch(
    localized_root: Path,
    source: dict[str, Any],
    resolved: dict[str, str],
) -> None:
    documents: dict[str, Any] = {}
    for entry in source.get("entries", []):
        uid = entry["uid"]
        source_path = entry["source_path"]
        json_path = entry["json_path"]
        kind = entry.get("kind")
        if kind == "asset":
            raise RuntimeError(
                f"asset batch requires file-complete handling and is not mergeable yet: {source_path}"
            )
        if source_path not in documents:
            target_path = localized_root / source_path
            documents[source_path] = _load_json(target_path, {})
        _set_path(documents[source_path], json_path, resolved[uid])
    for source_path, doc in documents.items():
        _write_json(localized_root / source_path, doc)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-ref", required=True)
    parser.add_argument("--results-root", type=Path, default=Path("work/results"))
    parser.add_argument("--merged-root", type=Path, default=Path("work/merged"))
    parser.add_argument("--localized-root", type=Path, default=Path("localized_data"))
    parser.add_argument("--progress", type=Path, default=Path("work/translation_progress.json"))
    args = parser.parse_args()

    args.merged_root.mkdir(parents=True, exist_ok=True)
    results = _collect_results(args.results_root)
    quality_guard = TranslationQualityGuard(Path("glossary"))
    newly_merged: list[int] = []
    diagnostics: dict[str, list[str]] = {}

    for batch in sorted(results):
        marker = args.merged_root / f"batch-{batch:05d}.json"
        if marker.exists():
            continue
        source = _source_batch(args.source_ref, batch)
        resolved, batch_diagnostics, claims = _validate_and_complete(
            source,
            args.source_ref,
            results[batch],
            quality_guard=quality_guard,
        )
        if resolved is None:
            diagnostics[str(batch)] = batch_diagnostics
            continue
        _apply_batch(args.localized_root, source, resolved)
        marker_payload = {
            "schema_version": 1,
            "batch": batch,
            "source_commit": source.get("source_commit"),
            "source_batch_ref": args.source_ref,
            "entry_count": len(source.get("entries", [])),
            "claim_ids": sorted(claims),
            "status": "merged",
        }
        _write_json(marker, marker_payload)
        claim_path = Path("work/claims") / f"batch-{batch:05d}.json"
        if claim_path.exists():
            claim_path.unlink()
        newly_merged.append(batch)

    progress = _load_json(args.progress, {})
    marker_files = sorted(args.merged_root.glob("batch-*.json"))
    merged_batches: list[int] = []
    translated_entries = 0
    for marker_file in marker_files:
        marker = _load_json(marker_file, {})
        if marker.get("status") != "merged":
            continue
        merged_batches.append(int(marker["batch"]))
        translated_entries += int(marker.get("entry_count", 0))

    progress["parallel_mode"] = True
    progress["translated_batches"] = merged_batches
    progress["reviewed_batches"] = merged_batches
    progress["qa_passed_batches"] = merged_batches
    progress["translated_entries"] = translated_entries
    total_batches = int(progress.get("queue_total_batches", 0) or 0)
    completed = set(merged_batches)
    next_unmerged = next((n for n in range(1, total_batches + 1) if n not in completed), None)
    progress["next_batch"] = next_unmerged
    parallel_state = progress.setdefault("parallel_state", {})
    parallel_state["next_unmerged_batch"] = next_unmerged
    parallel_state["completed_batches"] = len(merged_batches)
    _write_json(args.progress, progress)

    if diagnostics:
        _write_json(Path("work/merge_diagnostics.json"), diagnostics)
    elif Path("work/merge_diagnostics.json").exists():
        Path("work/merge_diagnostics.json").unlink()

    print(
        json.dumps(
            {
                "newly_merged": newly_merged,
                "merged_batches": len(merged_batches),
                "translated_entries": translated_entries,
                "next_unmerged_batch": next_unmerged,
                "incomplete_or_conflicted": sorted(int(k) for k in diagnostics),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

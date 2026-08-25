from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

SOURCE_REPO = "Hachimi-Hachimi/tl-zh-cn"
SOURCE_LANGUAGE = "zh-CN"
SOURCE_LICENSE = "CC BY-NC-SA 4.0"

DICT_KINDS = {
    "localize_dict.json": "ui",
    "text_data_dict.json": "text_data",
    "character_system_text_dict.json": "character_system",
    "race_jikkyo_comment_dict.json": "race_comment",
    "race_jikkyo_message_dict.json": "race_message",
    "hashed_dict.json": "hashed",
}
TRANSLATABLE_KEYS = {
    "text", "name", "title", "caption", "label", "message", "description", "choice_text", "ruby",
}
LIST_TEXT_KEYS = {"choice_data_list", "choices", "colored_text_info_list"}
SKIP_KEYS = {"hash", "bundle_hash", "asset_hash", "path", "cue_id", "id", "voice_id", "clip_length", "start_time"}
PRIORITY = {
    "ui": 0, "text_data": 1, "character_system": 2, "race_comment": 3, "race_message": 4,
    "hashed": 5, "lyrics": 6, "home": 7, "story": 8, "race_story": 9, "asset": 10,
}


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def pointer(path: list[Any]) -> str:
    if not path:
        return ""
    return "/" + "/".join(str(p).replace("~", "~0").replace("/", "~1") for p in path)


def kind_for_asset(rel: str) -> str:
    p = "/" + rel.replace("\\", "/").lower().lstrip("/")
    if "/lyrics/" in p:
        return "lyrics"
    if "/race/storyrace/" in p or "/storyrace/" in p:
        return "race_story"
    if "/home/" in p:
        return "home"
    if "/story/" in p:
        return "story"
    return "asset"


def make_record(*, rel: str, path: list[Any], source_text: str, kind: str, source_commit: str) -> dict[str, Any]:
    loc = f"{rel}#{pointer(path)}"
    uid = "zhcn:" + sha256_text(loc)[:24]
    return {
        "uid": uid,
        "kind": kind,
        "source_language": SOURCE_LANGUAGE,
        "source_text": source_text,
        "source_fingerprint": sha256_text(source_text),
        "source_repo": SOURCE_REPO,
        "source_commit": source_commit,
        "source_path": rel,
        "json_path": path,
        "json_pointer": pointer(path),
    }


def iter_all_string_leaves(node: Any, path: list[Any] | None = None) -> Iterable[tuple[list[Any], str]]:
    path = path or []
    if isinstance(node, dict):
        for key, value in node.items():
            child = [*path, key]
            if isinstance(value, str) and value.strip():
                yield child, value
            elif isinstance(value, (dict, list)):
                yield from iter_all_string_leaves(value, child)
    elif isinstance(node, list):
        for idx, value in enumerate(node):
            child = [*path, idx]
            if isinstance(value, str) and value.strip():
                yield child, value
            elif isinstance(value, (dict, list)):
                yield from iter_all_string_leaves(value, child)


def iter_asset_string_leaves(node: Any, path: list[Any] | None = None, parent_key: str | None = None) -> Iterable[tuple[list[Any], str]]:
    path = path or []
    if isinstance(node, dict):
        for key, value in node.items():
            if key in SKIP_KEYS:
                continue
            child = [*path, key]
            if isinstance(value, str) and value.strip() and key in TRANSLATABLE_KEYS:
                yield child, value
            elif isinstance(value, (dict, list)):
                yield from iter_asset_string_leaves(value, child, key)
    elif isinstance(node, list):
        for idx, value in enumerate(node):
            child = [*path, idx]
            if isinstance(value, str) and value.strip() and parent_key in LIST_TEXT_KEYS:
                yield child, value
            elif isinstance(value, (dict, list)):
                yield from iter_asset_string_leaves(value, child, parent_key)


def collect(upstream_root: Path, source_commit: str) -> tuple[list[dict[str, Any]], dict[str, int]]:
    localized = upstream_root / "localized_data"
    if not localized.is_dir():
        raise SystemExit(f"localized_data not found under {upstream_root}")
    records: list[dict[str, Any]] = []
    file_counts = {"scanned": 0, "with_entries": 0, "invalid_json": 0}
    seen_locators: set[tuple[str, str]] = set()
    for file in sorted(localized.rglob("*.json")):
        rel = file.relative_to(localized).as_posix()
        file_counts["scanned"] += 1
        try:
            doc = json.loads(file.read_text(encoding="utf-8-sig"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            file_counts["invalid_json"] += 1
            continue
        base = file.name.lower()
        if base in DICT_KINDS and "/" not in rel:
            kind = DICT_KINDS[base]
            leaves = iter_all_string_leaves(doc)
        else:
            kind = kind_for_asset(rel)
            leaves = iter_asset_string_leaves(doc)
        before = len(records)
        for json_path, text in leaves:
            locator = (rel, pointer(json_path))
            if locator in seen_locators:
                continue
            seen_locators.add(locator)
            records.append(make_record(rel=rel, path=json_path, source_text=text, kind=kind, source_commit=source_commit))
        if len(records) > before:
            file_counts["with_entries"] += 1
    records.sort(key=lambda r: (PRIORITY.get(r["kind"], 99), r["source_path"], canonical(r["json_path"])))
    return records, file_counts


def write_batches(records: list[dict[str, Any]], out_dir: Path, batch_size: int, source_commit: str, file_counts: dict[str, int]) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("batch-*.json"):
        old.unlink()
    batch_count = (len(records) + batch_size - 1) // batch_size if records else 0
    for idx in range(batch_count):
        chunk = records[idx * batch_size:(idx + 1) * batch_size]
        payload = {
            "schema_version": 1, "batch": idx + 1, "batch_count": batch_count,
            "source_repo": SOURCE_REPO, "source_commit": source_commit,
            "source_language": SOURCE_LANGUAGE, "entries": chunk,
        }
        (out_dir / f"batch-{idx + 1:05d}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    by_kind = Counter(r["kind"] for r in records)
    total_chars = sum(len(r["source_text"]) for r in records)
    manifest = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_repo": SOURCE_REPO,
        "source_branch": "dev",
        "source_commit": source_commit,
        "source_language": SOURCE_LANGUAGE,
        "source_license": SOURCE_LICENSE,
        "batch_size": batch_size,
        "total_batches": batch_count,
        "total_entries": len(records),
        "total_source_chars": total_chars,
        "by_kind": dict(sorted(by_kind.items())),
        "files": file_counts,
        "next_batch": "batch-00001.json" if batch_count else None,
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    progress = {
        "schema_version": 1,
        "source_commit": source_commit,
        "translated_batches": [],
        "reviewed_batches": [],
        "qa_passed_batches": [],
        "next_translation_batch": 1 if batch_count else None,
        "total_batches": batch_count,
    }
    (out_dir / "progress.template.json").write_text(json.dumps(progress, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize a Hachimi translation repo into stable source batches.")
    parser.add_argument("--upstream-root", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--batch-size", type=int, default=80)
    args = parser.parse_args()
    if args.batch_size < 1:
        parser.error("--batch-size must be >= 1")
    records, file_counts = collect(args.upstream_root, args.source_commit)
    manifest = write_batches(records, args.out, args.batch_size, args.source_commit, file_counts)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

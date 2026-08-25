from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

from ..model import SourceEntry, canonical_json
from ..store import Store


TRANSLATABLE_KEYS = {"title", "text", "name", "caption", "label"}
SKIP_KEYS = {"hash", "bundle_hash", "asset_hash", "path", "cue_id", "id"}


def _kind_for_path(rel: str) -> str:
    p = rel.replace("\\", "/").lower()
    if "/lyrics/" in f"/{p}":
        return "lyrics"
    if "/race/storyrace/" in f"/{p}":
        return "race_story"
    if "/home/" in f"/{p}":
        return "story"
    if "/story/" in f"/{p}":
        return "story"
    if "/uianimation/" in f"/{p}":
        return "ui_asset"
    return "asset"


def _json_path_uid(path: list[Any]) -> str:
    return "/".join(str(x).replace("/", "~1") for x in path)


def _is_lyrics_doc(doc: Any, rel: str) -> bool:
    normalized = rel.replace("\\", "/").lower()
    return "/lyrics/" in f"/{normalized}" and isinstance(doc, dict)


def _story_context(doc: dict[str, Any], block_index: int) -> dict[str, Any]:
    blocks = doc.get("text_block_list")
    if not isinstance(blocks, list):
        return {}
    block = blocks[block_index] if 0 <= block_index < len(blocks) else None
    context: dict[str, Any] = {"block_index": block_index}
    if isinstance(block, dict) and isinstance(block.get("name"), str):
        context["speaker"] = block["name"]
    for delta, label in ((-1, "previous"), (1, "next")):
        idx = block_index + delta
        if 0 <= idx < len(blocks) and isinstance(blocks[idx], dict):
            text = blocks[idx].get("text")
            if isinstance(text, str):
                context[label] = text
    return context


def _iter_entries(doc: Any, rel: str) -> Iterable[SourceEntry]:
    kind = _kind_for_path(rel)
    if _is_lyrics_doc(doc, rel):
        for key, value in doc.items():
            if isinstance(value, str) and value.strip():
                path = [str(key)]
                yield SourceEntry(
                    uid=f"asset:{rel}:{_json_path_uid(path)}",
                    kind="lyrics",
                    source_text=value,
                    locator={"asset_path": rel, "json_path": path},
                    context={"domain": "lyrics", "asset_path": rel, "timestamp": str(key)},
                )
        return

    def walk(node: Any, path: list[Any], parent_key: str | None = None):
        if isinstance(node, dict):
            for key, value in node.items():
                if key in SKIP_KEYS:
                    continue
                child_path = [*path, key]
                if isinstance(value, str) and key in TRANSLATABLE_KEYS and value.strip():
                    context: dict[str, Any] = {"domain": kind, "asset_path": rel, "field": key}
                    if len(path) >= 2 and path[-2] == "text_block_list" and isinstance(path[-1], int) and isinstance(doc, dict):
                        context.update(_story_context(doc, path[-1]))
                    yield SourceEntry(
                        uid=f"asset:{rel}:{_json_path_uid(child_path)}",
                        kind=kind,
                        source_text=value,
                        locator={"asset_path": rel, "json_path": child_path},
                        context=context,
                    )
                elif isinstance(value, (dict, list)):
                    yield from walk(value, child_path, key)
        elif isinstance(node, list):
            for i, value in enumerate(node):
                child_path = [*path, i]
                if isinstance(value, str) and parent_key in {"choice_data_list", "choices", "colored_text_info_list"} and value.strip():
                    context = {"domain": kind, "asset_path": rel, "field": parent_key or "list"}
                    if len(path) >= 2 and path[-2] == "text_block_list" and isinstance(path[-1], int) and isinstance(doc, dict):
                        context.update(_story_context(doc, path[-1]))
                    yield SourceEntry(
                        uid=f"asset:{rel}:{_json_path_uid(child_path)}",
                        kind=kind,
                        source_text=value,
                        locator={"asset_path": rel, "json_path": child_path},
                        context=context,
                    )
                elif isinstance(value, (dict, list)):
                    yield from walk(value, child_path, parent_key)

    yield from walk(doc, [])


def import_asset_directory(path: str | Path, store: Store) -> dict[str, int]:
    root = Path(path)
    counts: dict[str, int] = {}
    for file in sorted(root.rglob("*.json")):
        raw = file.read_text(encoding="utf-8")
        try:
            doc = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON asset: {file}: {exc}") from exc
        rel = file.relative_to(root).as_posix()
        sha = hashlib.sha256(canonical_json(doc).encode("utf-8")).hexdigest()
        store.upsert_asset_document(rel, canonical_json(doc), sha)
        entries = list(_iter_entries(doc, rel))
        if entries:
            store.upsert_entries(entries)
            for e in entries:
                counts[e.kind] = counts.get(e.kind, 0) + 1
    return counts

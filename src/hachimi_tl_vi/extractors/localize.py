from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..model import SourceEntry
from ..store import Store


def _iter_pairs(data: Any):
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, str):
                yield str(key), value
            elif isinstance(value, dict):
                text = value.get("text") or value.get("value") or value.get("source")
                if isinstance(text, str):
                    yield str(value.get("id", key)), text
    elif isinstance(data, list):
        for i, value in enumerate(data):
            if not isinstance(value, dict):
                continue
            key = value.get("id", value.get("key", i))
            text = value.get("text") or value.get("value") or value.get("source")
            if isinstance(text, str):
                yield str(key), text


def import_localize_dump(path: str | Path, store: Store) -> int:
    path = Path(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    entries = [
        SourceEntry(
            uid=f"localize:{key}",
            kind="localize",
            source_text=text,
            locator={"id": key},
            context={"domain": "ui", "source_file": path.name},
        )
        for key, text in _iter_pairs(data)
        if text.strip()
    ]
    return store.upsert_entries(entries)

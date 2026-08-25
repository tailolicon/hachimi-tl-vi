from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from .store import Store


def _set_json_path(doc: Any, path: list[Any], value: str) -> None:
    node = doc
    for segment in path[:-1]:
        node = node[segment]
    node[path[-1]] = value


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def compile_localized_data(store: Store, out_dir: str | Path = "localized_data") -> dict[str, int]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    localize: dict[str, str] = {}
    hashed: dict[str, str] = {}
    text_data: dict[str, dict[str, str]] = {}
    chara: dict[str, dict[str, str]] = {}
    race_comment: dict[str, str] = {}
    race_message: dict[str, str] = {}
    asset_translations: dict[str, list[tuple[list[Any], str]]] = {}

    counts: dict[str, int] = {}
    for entry, tl in store.entries_with_translation():
        counts[entry.kind] = counts.get(entry.kind, 0) + 1
        loc = entry.locator
        if entry.kind == "localize":
            localize[str(loc["id"])] = tl.target_text
        elif entry.kind == "hashed":
            hashed[str(loc["hash"])] = tl.target_text
        elif entry.kind == "text_data":
            text_data.setdefault(str(loc["category"]), {})[str(loc["index"])] = tl.target_text
        elif entry.kind == "character_system_text":
            chara.setdefault(str(loc["character_id"]), {})[str(loc["voice_id"])] = tl.target_text
        elif entry.kind == "race_jikkyo_comment":
            race_comment[str(loc["id"])] = tl.target_text
        elif entry.kind == "race_jikkyo_message":
            race_message[str(loc["id"])] = tl.target_text
        elif "asset_path" in loc and "json_path" in loc:
            asset_translations.setdefault(loc["asset_path"], []).append((loc["json_path"], tl.target_text))

    _write_json(out / "localize_dict.json", localize)
    _write_json(out / "hashed_dict.json", hashed)
    _write_json(out / "text_data_dict.json", text_data)
    _write_json(out / "character_system_text_dict.json", chara)
    _write_json(out / "race_jikkyo_comment_dict.json", race_comment)
    _write_json(out / "race_jikkyo_message_dict.json", race_message)

    for asset_path, source_doc in store.get_asset_documents():
        replacements = asset_translations.get(asset_path)
        if not replacements:
            continue
        doc = copy.deepcopy(source_doc)
        for json_path, text in replacements:
            _set_json_path(doc, json_path, text)
        _write_json(out / "assets" / asset_path, doc)

    return counts

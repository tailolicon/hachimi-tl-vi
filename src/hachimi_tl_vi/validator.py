from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .qa import qa_pair
from .store import Store


REQUIRED_FILES = [
    "config.json",
    "info.json",
    "localize_dict.json",
    "hashed_dict.json",
    "text_data_dict.json",
    "character_system_text_dict.json",
    "race_jikkyo_comment_dict.json",
    "race_jikkyo_message_dict.json",
]


def validate_json_tree(root: Path) -> list[str]:
    errors: list[str] = []
    for file in root.rglob("*.json"):
        try:
            json.loads(file.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"invalid_json:{file}:{exc}")
    return errors


def validate_project(store: Store | None = None, localized_dir: str | Path = "localized_data") -> dict[str, Any]:
    root = Path(localized_dir)
    errors: list[str] = []
    warnings: list[str] = []
    for name in REQUIRED_FILES:
        if not (root / name).is_file():
            errors.append(f"missing_file:{name}")
    errors.extend(validate_json_tree(root))

    info_path = root / "info.json"
    if info_path.exists():
        info = json.loads(info_path.read_text(encoding="utf-8"))
        if info.get("language") != "vi":
            errors.append("info_language_must_be_vi")

    if store is not None:
        for entry, tl in store.entries_with_translation():
            qa = qa_pair(entry.source_text, tl.target_text)
            for problem in qa["problems"]:
                if problem == "newline_count_changed":
                    warnings.append(f"{entry.uid}:{problem}")
                else:
                    errors.append(f"{entry.uid}:{problem}")

    return {"ok": not errors, "errors": errors, "warnings": warnings}

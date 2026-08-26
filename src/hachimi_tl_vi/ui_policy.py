from __future__ import annotations

import json
from pathlib import Path
import re
import unicodedata
from typing import Any

_TAG_RE = re.compile(r"<[^<>\r\n]+>")
_PLACEHOLDER_RE = re.compile(
    r"\{[^{}\r\n]+\}|%(?:\d+\$)?[-+0 #]*\d*(?:\.\d+)?[sdif]|\$[A-Za-z_][A-Za-z0-9_]*|\$\([^\)\r\n]+\)"
)
_SENTENCE_ENDINGS = set("。！？!?")
_CJK_RANGES = (
    (0x2E80, 0x2FFF),
    (0x3000, 0x303F),
    (0x3040, 0x30FF),
    (0x31F0, 0x31FF),
    (0x3400, 0x4DBF),
    (0x4E00, 0x9FFF),
    (0xF900, 0xFAFF),
)


def _is_cjk(char: str) -> bool:
    cp = ord(char)
    return any(start <= cp <= end for start, end in _CJK_RANGES)


def _visible_text(text: str) -> str:
    text = _TAG_RE.sub("", text)
    return _PLACEHOLDER_RE.sub("X", text)


def visual_units(text: str) -> float:
    """Approximate horizontal UI width in em-like units."""
    total = 0.0
    for char in _visible_text(text):
        if char == "\n":
            continue
        if unicodedata.combining(char):
            continue
        if _is_cjk(char):
            total += 1.0
        elif char.isspace():
            total += 0.32
        elif char in "/\\|·・-–—:;,.…'\"()[]{}":
            total += 0.36
        elif char.isdigit():
            total += 0.55
        else:
            total += 0.58
    return round(total, 3)


def assess_compact_ui(
    source: str,
    target: str,
    *,
    kind: str | None = None,
    source_path: str | None = None,
) -> dict[str, Any]:
    """Return heuristic warnings for short fixed-size UI labels."""
    warnings: list[str] = []
    if kind not in (None, "localize"):
        return {"checked": False, "warnings": warnings}
    if source_path not in (None, "localize_dict.json"):
        return {"checked": False, "warnings": warnings}
    if source.count("\n") != target.count("\n"):
        return {"checked": False, "warnings": warnings}

    source_lines = source.split("\n")
    target_lines = target.split("\n")
    checked = False

    for index, (src_line, dst_line) in enumerate(zip(source_lines, target_lines, strict=True), start=1):
        visible_src = _visible_text(src_line).strip()
        if not visible_src:
            continue
        src_units = visual_units(src_line)
        dst_units = visual_units(dst_line)
        if src_units <= 8.5 and len(visible_src) <= 18 and not any(c in _SENTENCE_ENDINGS for c in visible_src):
            checked = True
            budget = max(5.0, src_units * 1.55 + 0.5)
            if dst_units > budget:
                warnings.append(
                    f"line {index}: target visual width {dst_units:.2f} exceeds compact UI budget {budget:.2f}"
                )

    return {"checked": checked, "warnings": warnings}


def _get_path(document: Any, path: list[Any]) -> tuple[bool, Any]:
    node = document
    for segment in path:
        if isinstance(node, dict):
            key = str(segment)
            if key not in node:
                return False, None
            node = node[key]
        elif isinstance(node, list) and isinstance(segment, int) and 0 <= segment < len(node):
            node = node[segment]
        else:
            return False, None
    return True, node


def _set_path(document: Any, path: list[Any], value: str) -> bool:
    if not path:
        return False
    node = document
    for segment in path[:-1]:
        if isinstance(node, dict):
            key = str(segment)
            if key not in node:
                return False
            node = node[key]
        elif isinstance(node, list) and isinstance(segment, int) and 0 <= segment < len(node):
            node = node[segment]
        else:
            return False

    final = path[-1]
    if isinstance(node, dict):
        key = str(final)
        if key not in node:
            return False
        node[key] = value
        return True
    if isinstance(node, list) and isinstance(final, int) and 0 <= final < len(node):
        node[final] = value
        return True
    return False


def _replace_exact(node: Any, old: str, new: str) -> int:
    count = 0
    if isinstance(node, dict):
        for key, value in list(node.items()):
            if isinstance(value, str) and value == old:
                node[key] = new
                count += 1
            else:
                count += _replace_exact(value, old, new)
    elif isinstance(node, list):
        for index, value in enumerate(node):
            if isinstance(value, str) and value == old:
                node[index] = new
                count += 1
            else:
                count += _replace_exact(value, old, new)
    return count


def apply_ui_overrides(repo_root: Path, *, write: bool = True) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    policy_path = repo_root / "glossary" / "ui_overrides.json"
    localized_root = repo_root / "localized_data"
    policy = json.loads(policy_path.read_text(encoding="utf-8"))

    docs: dict[str, Any] = {}
    changed_files: set[str] = set()
    key_changes = 0
    exact_changes = 0
    missing_keys: list[str] = []

    def get_doc(filename: str) -> Any:
        if filename not in docs:
            docs[filename] = json.loads((localized_root / filename).read_text(encoding="utf-8"))
        return docs[filename]

    for item in policy.get("key_overrides", []):
        filename = str(item["file"])
        path = list(item["path"])
        text = str(item["text"])
        document = get_doc(filename)
        exists, current = _get_path(document, path)
        if not exists:
            missing_keys.append(f"{filename}:{path!r}")
            continue
        if current != text and _set_path(document, path, text):
            key_changes += 1
            changed_files.add(filename)

    for item in policy.get("exact_replacements", []):
        old = str(item["from"])
        new = str(item["to"])
        for filename in item.get("files", ["localize_dict.json"]):
            document = get_doc(str(filename))
            count = _replace_exact(document, old, new)
            if count:
                exact_changes += count
                changed_files.add(str(filename))

    if write:
        for filename in sorted(changed_files):
            path = localized_root / filename
            path.write_text(
                json.dumps(docs[filename], ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
                newline="\n",
            )

    return {
        "schema_version": 1,
        "changed_files": sorted(changed_files),
        "key_changes": key_changes,
        "exact_changes": exact_changes,
        "total_changes": key_changes + exact_changes,
        "missing_keys": missing_keys,
        "write": write,
    }

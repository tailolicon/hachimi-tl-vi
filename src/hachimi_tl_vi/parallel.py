from __future__ import annotations

from collections import Counter
import re
from typing import Any

_BRACE_PLACEHOLDER_RE = re.compile(r"\{[^{}\r\n]+\}")
_PRINTF_PLACEHOLDER_RE = re.compile(r"%(?:\d+\$)?[-+0 #]*\d*(?:\.\d+)?[sdif]")
_TAG_RE = re.compile(r"<[^<>\r\n]+>")
_ESCAPED_RUNTIME_RE = re.compile(r"\\[nrt]")


def runtime_token_counters(text: str) -> dict[str, Counter[str]]:
    return {
        "brace_placeholders": Counter(_BRACE_PLACEHOLDER_RE.findall(text)),
        "printf_placeholders": Counter(_PRINTF_PLACEHOLDER_RE.findall(text)),
        "tags": Counter(_TAG_RE.findall(text)),
        "escaped_runtime": Counter(_ESCAPED_RUNTIME_RE.findall(text)),
    }


def structural_qa(source: str, target: str) -> dict[str, Any]:
    source_tokens = runtime_token_counters(source)
    target_tokens = runtime_token_counters(target)
    errors: list[str] = []
    for key in source_tokens:
        if source_tokens[key] != target_tokens[key]:
            errors.append(f"{key} differ")
    if source.count("\n") != target.count("\n"):
        errors.append("newline count differs")
    return {
        "passed": not errors,
        "errors": errors,
        "source_newlines": source.count("\n"),
        "target_newlines": target.count("\n"),
    }


def set_json_path(document: Any, path: list[Any], value: str) -> None:
    if not path:
        raise ValueError("json_path must not be empty")

    node = document
    for index, segment in enumerate(path[:-1]):
        next_segment = path[index + 1]
        if isinstance(node, list):
            if not isinstance(segment, int):
                raise TypeError(f"list path segment must be int, got {segment!r}")
            while len(node) <= segment:
                node.append(None)
            child = node[segment]
            if not isinstance(child, (dict, list)):
                child = [] if isinstance(next_segment, int) else {}
                node[segment] = child
            node = child
        elif isinstance(node, dict):
            key = str(segment)
            child = node.get(key)
            if not isinstance(child, (dict, list)):
                child = [] if isinstance(next_segment, int) else {}
                node[key] = child
            node = child
        else:
            raise TypeError(f"cannot traverse through {type(node).__name__}")

    final = path[-1]
    if isinstance(node, list):
        if not isinstance(final, int):
            raise TypeError(f"list path segment must be int, got {final!r}")
        while len(node) <= final:
            node.append(None)
        node[final] = value
    elif isinstance(node, dict):
        node[str(final)] = value
    else:
        raise TypeError(f"cannot assign through {type(node).__name__}")


def task_id(batch: int, shard: int) -> str:
    return f"batch-{batch:05d}-s{shard:02d}"


def task_group(batch: int) -> str:
    return f"b{batch // 100:04d}"


def task_slice(entry_count: int, shard: int, task_size: int) -> tuple[int, int]:
    if shard < 0:
        raise ValueError("shard must be >= 0")
    if task_size < 1:
        raise ValueError("task_size must be >= 1")
    start = shard * task_size
    return start, min(start + task_size, entry_count)

from __future__ import annotations

import re

TOKEN_PATTERNS = [
    re.compile(r"\{[^{}]+\}"),
    re.compile(r"</?[^<>]+>"),
    re.compile(r"\$\([^)]*\)"),
    re.compile(r"\$[A-Za-z_][A-Za-z0-9_]*"),
    re.compile(r"%(?:\d+\$)?[sdif]"),
]


def technical_tokens(text: str) -> list[str]:
    tokens: list[str] = []
    for pattern in TOKEN_PATTERNS:
        tokens.extend(pattern.findall(text))
    return sorted(tokens)


def qa_pair(source: str, target: str) -> dict[str, object]:
    src_tokens = technical_tokens(source)
    dst_tokens = technical_tokens(target)
    problems: list[str] = []
    if src_tokens != dst_tokens:
        problems.append("placeholder_mismatch")
    if source.count("\n") != target.count("\n"):
        problems.append("newline_count_changed")
    if not target.strip():
        problems.append("empty_translation")
    return {
        "ok": not problems,
        "problems": problems,
        "source_tokens": src_tokens,
        "target_tokens": dst_tokens,
    }

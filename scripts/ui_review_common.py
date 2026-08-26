from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from typing import Any

_TAG_RE = re.compile(r"<[^<>\r\n]+>")
_BRACE_RE = re.compile(r"\{[^{}\r\n]+\}")
_PRINTF_RE = re.compile(r"%(?:\d+\$)?[-+0 #]*\d*(?:\.\d+)?[sdif]")
_RUNTIME_RE = re.compile(r"\$\([^)]*\)|\$[A-Za-z_][A-Za-z0-9_]*")
_CJK_RE = re.compile(r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff]")
_LETTER_SLASH_RE = re.compile(r"[^\W\d_]\s*/\s*[^\W\d_]", re.UNICODE)


def load_json(path: Path, default: Any | None = None) -> Any:
    if not path.exists():
        if default is not None:
            return default
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def parse_utc(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def text_fingerprint(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _visible_text(text: str) -> str:
    value = _TAG_RE.sub("", text)
    value = _BRACE_RE.sub("X", value)
    value = _PRINTF_RE.sub("X", value)
    value = _RUNTIME_RE.sub("X", value)
    return value


def visual_width(text: str) -> float:
    widths: list[float] = []
    for line in _visible_text(text).split("\n"):
        total = 0.0
        for ch in line:
            code = ord(ch)
            if ch.isspace():
                total += 0.33
            elif 0x3040 <= code <= 0x30FF or 0x3400 <= code <= 0x4DBF or 0x4E00 <= code <= 0x9FFF:
                total += 1.0
            elif ch.isalpha() or ch.isdigit():
                total += 0.58
            else:
                total += 0.38
        widths.append(total)
    return max(widths, default=0.0)


def contains_cjk(text: str) -> bool:
    return bool(_CJK_RE.search(_visible_text(text)))


def risk_flags(source: str, target: str) -> list[str]:
    flags: list[str] = []
    source_w = visual_width(source)
    target_w = visual_width(target)
    budget = max(5.0, source_w * 1.55 + 0.5)
    if target_w > budget:
        flags.append("overflow_risk")
    if _LETTER_SLASH_RE.search(target):
        flags.append("slash_compound")
    if contains_cjk(target):
        flags.append("source_script_leakage")
    if target.count("\n") != source.count("\n"):
        flags.append("newline_mismatch")
    lower = target.lower()
    for phrase in ("thực tế", "chức năng", "dành cho", "được dùng để", "chuyển đổi"):
        if phrase in lower:
            flags.append("verbose_wording")
            break
    if target_w >= 16.0:
        flags.append("wide_label")
    return flags


def is_review_candidate(source: str, target: str) -> bool:
    """Return only likely fixed-size UI labels/controls, not general localize prose."""
    if not isinstance(source, str) or not isinstance(target, str):
        return False
    if not source.strip() or not target.strip() or source == target:
        return False
    if source.count("\n") > 1 or target.count("\n") > 2:
        return False

    source_visible = _visible_text(source).strip()
    target_visible = _visible_text(target).strip()
    if not source_visible or not target_visible:
        return False

    # Strong prose signals. The UI pipeline deliberately leaves body/help/story
    # wording to normal translation QA rather than shortening it as a label.
    if any(mark in source_visible for mark in ("。", "！", "？", "，")):
        return False
    if source_visible.startswith(("・", "※", "●", "■")):
        return False

    # Japanese/Chinese fixed controls are typically very compact. Keeping this
    # threshold strict is preferable to reviewing thousands of system sentences.
    if visual_width(source) > 12.0:
        return False
    if len(source_visible.replace("\n", "")) > 24:
        return False

    # If the target added multiple lines to a one-line source, that is itself a
    # layout regression worth reviewing, so do not exclude it here.
    return True


def risk_score(source: str, target: str) -> int:
    weights = {
        "overflow_risk": 5,
        "newline_mismatch": 5,
        "source_script_leakage": 4,
        "slash_compound": 3,
        "verbose_wording": 2,
        "wide_label": 1,
    }
    return sum(weights.get(flag, 1) for flag in risk_flags(source, target))

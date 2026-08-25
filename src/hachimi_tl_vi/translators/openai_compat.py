from __future__ import annotations

import json
import os
import re
from typing import Sequence, Any

import httpx

from ..model import SourceEntry
from .base import Translator
from .prompt import build_messages


_JSON_FENCE = re.compile(r"^```(?:json)?\s*(.*?)\s*```$", re.S | re.I)


def _extract_json(text: str) -> Any:
    text = text.strip()
    match = _JSON_FENCE.match(text)
    if match:
        text = match.group(1).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            return json.loads(text[start:end + 1])
        raise


class OpenAICompatibleTranslator(Translator):
    def __init__(
        self,
        *,
        api_base: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
        temperature: float | None = None,
        timeout: float | None = None,
        glossary_dir: str = "glossary",
    ) -> None:
        self.api_base = (api_base or os.getenv("TLVI_API_BASE", "https://api.openai.com/v1")).rstrip("/")
        self.api_key = api_key if api_key is not None else os.getenv("TLVI_API_KEY", "")
        self.model = model or os.getenv("TLVI_MODEL", "gpt-5.6")
        self.temperature = float(temperature if temperature is not None else os.getenv("TLVI_TEMPERATURE", "0.2"))
        self.timeout = float(timeout if timeout is not None else os.getenv("TLVI_TIMEOUT", "120"))
        self.glossary_dir = glossary_dir

    def translate_batch(self, entries: Sequence[SourceEntry]) -> dict[str, str]:
        if not entries:
            return {}
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        payload = {
            "model": self.model,
            "messages": build_messages(entries, self.glossary_dir),
            "temperature": self.temperature,
        }
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(f"{self.api_base}/chat/completions", headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ValueError(f"Unexpected OpenAI-compatible response: {data}") from exc
        parsed = _extract_json(content)
        items = parsed.get("translations") if isinstance(parsed, dict) else None
        if not isinstance(items, list):
            raise ValueError("Translator response missing translations array")
        allowed = {e.uid for e in entries}
        result: dict[str, str] = {}
        for item in items:
            if not isinstance(item, dict):
                continue
            uid = item.get("id")
            text = item.get("text")
            if uid in allowed and isinstance(text, str):
                result[uid] = text
        missing = allowed - result.keys()
        if missing:
            raise ValueError(f"Translator omitted {len(missing)} items: {sorted(missing)[:5]}")
        return result

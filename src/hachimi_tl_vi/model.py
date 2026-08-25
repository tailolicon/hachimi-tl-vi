from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
from typing import Any


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


@dataclass(slots=True)
class SourceEntry:
    uid: str
    kind: str
    source_text: str
    locator: dict[str, Any]
    context: dict[str, Any] = field(default_factory=dict)

    @property
    def fingerprint(self) -> str:
        payload = {
            "kind": self.kind,
            "source_text": self.source_text,
            "context": self.context,
        }
        return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


@dataclass(slots=True)
class Translation:
    fingerprint: str
    target_text: str
    status: str = "translated"
    provider: str = "unknown"
    model: str = "unknown"
    qa: dict[str, Any] = field(default_factory=dict)

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

DEFERRED_IDENTITIES = [
    {
        "decision_id": "audit.finding.staho-tv-defer",
        "source_zh_cn": "スタホTV",
        "action": "defer",
        "target_vi": "",
        "kind": "system_label",
        "category": "system",
        "note": "SEGA/JP evidence confirms the Japanese feature spelling スタホTV, but current repository/reference evidence does not establish a sufficiently authoritative Latin/English player-facing identity. Preserve the finding as blocking rather than guess StarHo TV/StarHorse TV.",
    },
    {
        "decision_id": "audit.finding.hot-blooded-oath-defer",
        "source_zh_cn": "热血誓言",
        "action": "defer",
        "target_vi": "",
        "kind": "proper_name",
        "category": "condition",
        "note": "Targeted repository/reference checks do not yet establish the underlying JP/Global named identity with enough confidence. Do not turn the zh-CN semantic bridge into a project-wide literal translation.",
    },
    {
        "decision_id": "audit.finding.heroic-radiance-defer",
        "source_zh_cn": "英雄的光辉",
        "action": "defer",
        "target_vi": "",
        "kind": "proper_name",
        "category": "system",
        "note": "Current evidence is insufficient to distinguish a stable named player-facing identity from a zh-CN semantic rendering. Keep blocking until JP/Global identity is verified.",
    },
    {
        "decision_id": "audit.finding-awaiting-spring-bud-defer",
        "source_zh_cn": "待春之蕾",
        "action": "defer",
        "target_vi": "",
        "kind": "proper_name",
        "category": "system",
        "note": "Current evidence does not establish a verified international/official identity. Do not canonize a literal Vietnamese calque from the zh-CN bridge.",
    },
]


def _load(path: Path, default: dict[str, Any] | None = None) -> dict[str, Any]:
    if not path.exists():
        return dict(default or {})
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def _upsert(items: list[Any], record: dict[str, Any]) -> None:
    decision_id = str(record["decision_id"])
    for index, item in enumerate(items):
        if isinstance(item, dict) and str(item.get("decision_id") or "") == decision_id:
            merged = dict(item)
            merged.update(record)
            items[index] = merged
            return
    items.append(dict(record))


def harden(repo_root: Path = ROOT) -> bool:
    path = repo_root / "glossary" / "terminology_reviews.json"
    payload = _load(path, {"schema_version": 1, "decisions": []})
    decisions = payload.setdefault("decisions", [])
    if not isinstance(decisions, list):
        raise ValueError("glossary/terminology_reviews.json decisions must be a list")
    before = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    for record in DEFERRED_IDENTITIES:
        _upsert(decisions, record)
    if before == json.dumps(payload, ensure_ascii=False, sort_keys=True):
        return False
    _write(path, payload)
    return True


def main() -> int:
    changed = harden(ROOT)
    print(f"unverified_identity_defers_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

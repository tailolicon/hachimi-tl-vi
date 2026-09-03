from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TERM_ID = "common.stat.power"
NARRATIVE_EXCLUSIONS = [
    "强大力量",
    "商品的力量",
    "不可思议力量",
    "超越极限力量",
    "莱茵力量",
    "将情谊化为力量",
    "力量的传道者",
    "充满力量的乐曲",
    "将最大力量献给你",
    "宿敌赋予了我们力量",
    "依靠尾巴来支撑自己的力量",
]


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def harden(repo_root: Path = ROOT) -> bool:
    path = repo_root / "glossary" / "ui_community_terms.json"
    payload = _load(path)
    terms = payload.get("terms", [])
    if not isinstance(terms, list):
        raise ValueError("glossary/ui_community_terms.json terms must be a list")

    before = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    matched = False
    for term in terms:
        if not isinstance(term, dict) or term.get("id") != TERM_ID:
            continue
        matched = True
        existing = [str(value) for value in term.get("exclude_source_contains", []) if str(value)]
        term["exclude_source_contains"] = list(dict.fromkeys([*existing, *NARRATIVE_EXCLUSIONS]))
        term["basis"] = (
            "Common EN-version Power stat label. The zh-CN alias 力量 is ambiguous in ordinary prose and can also "
            "occur inside proper names such as 莱茵力量 (Rhein Kraft); known non-stat compounds, names, descriptive "
            "titles, and narrative/metaphorical phrases are explicitly excluded so physical or emotional strength "
            "is not normalized to the stat label."
        )
        break
    if not matched:
        raise ValueError(f"missing canonical community term {TERM_ID}")

    changed = before != json.dumps(payload, ensure_ascii=False, sort_keys=True)
    if changed:
        _write(path, payload)
    return changed


def main() -> int:
    changed = harden(ROOT)
    print(f"power_context_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

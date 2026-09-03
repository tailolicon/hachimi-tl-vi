from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TERM = {
    "id": "common.aptitude.zhcn_variant",
    "category": "system",
    "source_aliases": ["适应性", "资质"],
    "preferred": "Aptitude",
    "compact": [],
    "accepted": ["Aptitude"],
    "forbidden": ["Độ thích nghi", "độ thích nghi", "Thích nghi", "thích nghi"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["localize_dict.json"],
    "match_mode": "contains",
    "basis": "zh-CN localize UI uses 适应性 and 资质 as variants for the player-facing Aptitude system. Scope is restricted to localize_dict so generic adaptability prose elsewhere is not captured.",
}


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
    terms = payload.setdefault("terms", [])
    if not isinstance(terms, list):
        raise ValueError("glossary/ui_community_terms.json terms must be a list")
    before = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    for index, item in enumerate(terms):
        if isinstance(item, dict) and item.get("id") == TERM["id"]:
            merged = dict(item)
            merged.update(TERM)
            terms[index] = merged
            break
    else:
        terms.append(dict(TERM))
    changed = before != json.dumps(payload, ensure_ascii=False, sort_keys=True)
    if changed:
        _write(path, payload)
    return changed


def main() -> int:
    changed = harden(ROOT)
    print(f"aptitude_alias_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

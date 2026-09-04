from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

EXCLUSIONS = {
    "common.stat.power": ["获得相应的力量", "坚定不移的力量", "力量感"],
    "common.stat.speed": ["融会贯通的速度", "跳过速度", "成长速度"],
    "common.stat.guts": ["充满毅力"],
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
    terms = payload.get("terms", [])
    if not isinstance(terms, list):
        raise ValueError("community terms must be a list")
    before = json.dumps(payload, ensure_ascii=False, sort_keys=True)

    by_id = {str(term.get("id") or ""): term for term in terms if isinstance(term, dict)}
    for term_id, phrases in EXCLUSIONS.items():
        term = by_id.get(term_id)
        if term is None:
            raise ValueError(f"missing canonical term {term_id}")
        exclusions = term.setdefault("exclude_source_contains", [])
        if not isinstance(exclusions, list):
            raise ValueError(f"{term_id} exclude_source_contains must be a list")
        for phrase in phrases:
            if phrase not in exclusions:
                exclusions.append(phrase)

    changed = before != json.dumps(payload, ensure_ascii=False, sort_keys=True)
    if changed:
        _write(path, payload)
    return changed


def main() -> int:
    print(f"narrative_stat_context_hardening_changed={str(harden(ROOT)).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

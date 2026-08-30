from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TERM_ID = "reviewed.condition.97c2a1f26a21"


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def harden(repo_root: Path = ROOT) -> bool:
    path = repo_root / "glossary" / "term_registry.json"
    payload = _load(path)
    terms = payload.get("terms", [])
    if not isinstance(terms, list):
        raise ValueError("glossary/term_registry.json terms must be a list")
    before = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    matched = False
    for term in terms:
        if not isinstance(term, dict) or term.get("id") != TERM_ID:
            continue
        matched = True
        term["match_mode"] = "exact"
        term["source_paths"] = ["text_data_dict.json"]
        term["json_path_prefixes"] = [["142"]]
        term["invalidation_scope"] = "item"
        term["context_note"] = (
            "恢复精神 is the named Recovery Spirit Condition only in the text_data category-142 Condition-name table. "
            "Do not match the same words inside ordinary item prose such as 喝了恢复精神吧."
        )
        break
    if not matched:
        raise ValueError(f"missing canonical term {TERM_ID}")
    changed = before != json.dumps(payload, ensure_ascii=False, sort_keys=True)
    if changed:
        _write(path, payload)
    return changed


def main() -> int:
    changed = harden(ROOT)
    print(f"recovery_spirit_context_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

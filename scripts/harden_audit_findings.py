from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

NIGHT_OWL_REFERENCE_VARIANT = {
    "id": "common.condition.night_owl.reference_variant",
    "category": "condition",
    "source_aliases": ["熬夜倾向"],
    "preferred": "Night Owl",
    "compact": [],
    "accepted": ["Night Owl"],
    "forbidden": ["Xu hướng thức khuya", "Thức khuya"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [["143"]],
    "match_mode": "contains",
    "basis": "Named Night Owl Condition reference variant found during retrospective audit; scoped to text_data category 143 so ordinary prose about staying up late is not canonicalized.",
}


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _upsert(items: list[Any], record: dict[str, Any]) -> None:
    record_id = str(record["id"])
    for index, item in enumerate(items):
        if isinstance(item, dict) and str(item.get("id") or "") == record_id:
            merged = dict(item)
            merged.update(record)
            items[index] = merged
            return
    items.append(record)


def harden(repo_root: Path = ROOT) -> bool:
    path = repo_root / "glossary/ui_community_terms.json"
    payload = _load(path)
    before = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    terms = payload.setdefault("terms", [])
    if not isinstance(terms, list):
        raise ValueError("glossary/ui_community_terms.json terms must be a list")
    _upsert(terms, NIGHT_OWL_REFERENCE_VARIANT)
    after = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    if before == after:
        return False
    _write(path, payload)
    return True


def main() -> int:
    changed = harden(ROOT)
    print(f"audit_finding_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

STAMINA_THRESHOLD = {
    "id": "stat.stamina.achievement_threshold",
    "category": "stat",
    "source_aliases": ["体力"],
    "preferred": "Stamina",
    "compact": [],
    "accepted": ["Stamina"],
    "forbidden": ["Thể lực"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [["131"]],
    "match_mode": "contains",
    "basis": "In text_data category 131 achievement conditions, bracketed 体力 with a numeric threshold such as 1200 is the trainable Stamina stat. The training energy gauge cannot take four-digit stat values. Scope is restricted to achievement-condition category 131 so ordinary 体力 meaning Energy/physical condition elsewhere is unaffected. This is deliberately a scoped community rule, not a global reviewed lock, because the repository already canonically maps generic 体力 to Energy.",
}


def _load(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return dict(default)
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def _upsert(items: list[Any], record: dict[str, Any], *, id_field: str) -> None:
    record_id = str(record[id_field])
    for index, item in enumerate(items):
        if isinstance(item, dict) and str(item.get(id_field) or "") == record_id:
            merged = dict(item)
            merged.update(record)
            items[index] = merged
            return
    items.append(dict(record))


def harden(repo_root: Path = ROOT) -> bool:
    community_path = repo_root / "glossary" / "ui_community_terms.json"
    community = _load(community_path, {"schema_version": 1, "terms": []})
    before = json.dumps(community, ensure_ascii=False, sort_keys=True)
    _upsert(community.setdefault("terms", []), STAMINA_THRESHOLD, id_field="id")
    if before == json.dumps(community, ensure_ascii=False, sort_keys=True):
        return False
    _write(community_path, community)
    return True


def main() -> int:
    changed = harden(ROOT)
    print(f"stamina_threshold_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

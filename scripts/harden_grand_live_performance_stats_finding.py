from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

STATS = [
    ("visual", "形象值", "Visual", ["Hình tượng", "điểm Hình tượng"]),
    ("vocal", "声音值", "Vocal", ["Giọng hát", "điểm Giọng hát"]),
    ("passion", "热情值", "Passion", ["Nhiệt huyết", "điểm Nhiệt huyết"]),
]


def _load(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return dict(default)
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def _upsert(items: list[Any], record: dict[str, Any], id_field: str) -> None:
    rid = str(record[id_field])
    for index, item in enumerate(items):
        if isinstance(item, dict) and str(item.get(id_field) or "") == rid:
            merged = dict(item)
            merged.update(record)
            items[index] = merged
            return
    items.append(dict(record))


def harden(repo_root: Path = ROOT) -> bool:
    community_path = repo_root / "glossary/ui_community_terms.json"
    community = _load(community_path, {"schema_version": 1, "terms": []})
    terms = community.setdefault("terms", [])
    if not isinstance(terms, list):
        raise ValueError("canonical term collection must be a list")
    before = json.dumps(community, ensure_ascii=False, sort_keys=True)
    for slug, source, target, forbidden in STATS:
        _upsert(
            terms,
            {
                "id": f"scenario.grand_live.performance.{slug}.text_data",
                "category": "scenario",
                "source_aliases": [source],
                "preferred": target,
                "compact": [],
                "accepted": [target],
                "forbidden": forbidden,
                "require_accepted": True,
                "invalidation_scope": "item",
                "source_paths": ["text_data_dict.json"],
                "json_path_prefixes": [],
                "match_mode": "contains",
                "basis": f"Grand Live performance stat {source} is the named {target} category; source-path scope matches the active finding while avoiding unrelated files.",
            },
            "id",
        )
    changed = before != json.dumps(community, ensure_ascii=False, sort_keys=True)
    if changed:
        _write(community_path, community)
    return changed


def main() -> int:
    changed = harden(ROOT)
    print(f"grand_live_performance_stats_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

"""Canonicalize the zh-CN 牵绊值 variant as the Support Card Friendship Gauge."""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FINDING_ID = "cf-55673a272df0aaae"
LOCKED_TERM_ID = "progress.friendship_gauge.support_effects"
COMMUNITY_TERM_ID = "common.friendship_gauge.support_effects"
SOURCE_ALIAS = "牵绊值"
GENERIC_CALQUES = [
    "Điểm liên kết",
    "điểm liên kết",
    "Giá trị liên kết",
    "giá trị liên kết",
    "Gắn kết",
    "gắn kết",
]


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def _append_unique(values: Any, additions: list[str]) -> list[str]:
    current = [str(value) for value in values if str(value)] if isinstance(values, list) else []
    return list(dict.fromkeys([*current, *additions]))


def _find(terms: Any, term_id: str) -> dict[str, Any]:
    if not isinstance(terms, list):
        raise ValueError("glossary terms must be a list")
    for term in terms:
        if isinstance(term, dict) and str(term.get("id") or "") == term_id:
            return term
    raise ValueError(f"missing canonical term {term_id}")


def harden(repo_root: Path = ROOT) -> bool:
    registry_path = repo_root / "glossary" / "term_registry.json"
    community_path = repo_root / "glossary" / "ui_community_terms.json"
    registry = _load(registry_path)
    community = _load(community_path)
    before = json.dumps([registry, community], ensure_ascii=False, sort_keys=True)

    locked = _find(registry.get("terms", []), LOCKED_TERM_ID)
    locked["zh_cn"] = _append_unique(locked.get("zh_cn", []), [SOURCE_ALIAS])
    locked["source_paths"] = ["text_data_dict.json"]
    locked["json_path_prefixes"] = [["155"]]
    locked["match_mode"] = "contains"
    locked["invalidation_scope"] = "item"
    locked["note"] = (
        "Support-effect descriptions in text_data category 155 use 羁绊值/牵绊值 for the "
        "Support Card Friendship Gauge. Do not generalize bare friendship/bond prose to this system label."
    )

    term = _find(community.get("terms", []), COMMUNITY_TERM_ID)
    term["source_aliases"] = _append_unique(term.get("source_aliases", []), [SOURCE_ALIAS])
    term["forbidden"] = _append_unique(term.get("forbidden", []), GENERIC_CALQUES)
    term["source_paths"] = ["text_data_dict.json"]
    term["json_path_prefixes"] = [["155"]]
    term["match_mode"] = "contains"
    term["invalidation_scope"] = "item"
    term["basis"] = (
        "Category 155 support-effect descriptions use 羁绊值/牵绊值 for the Support Card Friendship Gauge. "
        "The category guard prevents ordinary friendship/bond prose from being normalized to this mechanic."
    )

    changed = before != json.dumps([registry, community], ensure_ascii=False, sort_keys=True)
    if changed:
        _write(registry_path, registry)
        _write(community_path, community)
    return changed


def main() -> int:
    print(f"friendship_gauge_variant_hardening_changed={str(harden(ROOT)).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

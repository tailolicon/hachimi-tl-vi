from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CANONICAL_TARGET = "Star Ascension"

# Compatibility hardener for the older Talent Bloom rule IDs. These IDs are
# already durable in generated registries, so keep them but migrate their
# target to the current canonical player-facing label instead of allowing the
# later alphabetic hardener pass to re-introduce the obsolete wording.
TALENT_BLOOM_CATEGORY_114 = {
    "id": "system.talent_bloom.text114",
    "category": "system_label",
    "source_aliases": ["才能开花"],
    "preferred": CANONICAL_TARGET,
    "compact": [],
    "accepted": [CANONICAL_TARGET],
    "forbidden": ["Talent Bloom", "Nở rộ tài năng", "nở rộ tài năng", "Khai hoa tài năng", "khai hoa tài năng"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [["114"]],
    "match_mode": "contains",
    "basis": "Compatibility rule for the named star-rarity progression mechanic. Released Global terminology is Star Ascension; keep the historical rule id but no longer emit the obsolete Talent Bloom target. Scope remains category 114 so the unrelated Skill title 开花 cannot bleed into progression prose.",
}

TALENT_BLOOM_LOCALIZE = {
    "id": "system.talent_bloom.localize",
    "category": "system_label",
    "source_aliases": ["才能开花"],
    "preferred": CANONICAL_TARGET,
    "compact": [],
    "accepted": [CANONICAL_TARGET],
    "forbidden": ["Talent Bloom", "Nở rộ tài năng", "nở rộ tài năng", "Khai hoa tài năng", "khai hoa tài năng"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["localize_dict.json"],
    "match_mode": "exact",
    "basis": "Compatibility rule for standalone localize labels using the complete 才能开花 phrase. Released Global terminology is Star Ascension. Exact phrase matching keeps the separate Skill title 开花 and generic bloom prose unaffected while covering legacy worker findings that were reported source-path-wide.",
}

TALENT_BLOOM_DECISION = {
    "decision_id": "audit.finding.talent-bloom-system",
    "source_zh_cn": "才能开花",
    "action": "lock",
    "target_vi": CANONICAL_TARGET,
    "kind": "system_label",
    "category": "system_label",
    "note": "Compatibility migration: 才能开花 uses released Global player-facing label Star Ascension, superseding the obsolete Talent Bloom wording. The separate Skill title 开花 remains exact-only.",
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


def _upsert(items: list[Any], record: dict[str, Any], id_field: str) -> None:
    record_id = str(record[id_field])
    for index, item in enumerate(items):
        if isinstance(item, dict) and str(item.get(id_field) or "") == record_id:
            merged = dict(item)
            merged.update(record)
            items[index] = merged
            return
    items.append(dict(record))


def harden(repo_root: Path = ROOT) -> bool:
    changed = False
    community_path = repo_root / "glossary" / "ui_community_terms.json"
    community = _load(community_path, {"schema_version": 1, "terms": []})
    terms = community.setdefault("terms", [])
    if not isinstance(terms, list):
        raise ValueError("glossary/ui_community_terms.json terms must be a list")
    before = json.dumps(community, ensure_ascii=False, sort_keys=True)
    _upsert(terms, TALENT_BLOOM_CATEGORY_114, "id")
    _upsert(terms, TALENT_BLOOM_LOCALIZE, "id")
    if before != json.dumps(community, ensure_ascii=False, sort_keys=True):
        _write(community_path, community)
        changed = True

    reviews_path = repo_root / "glossary" / "terminology_reviews.json"
    reviews = _load(reviews_path, {"schema_version": 1, "decisions": []})
    decisions = reviews.setdefault("decisions", [])
    if not isinstance(decisions, list):
        raise ValueError("glossary/terminology_reviews.json decisions must be a list")
    before = json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    _upsert(decisions, TALENT_BLOOM_DECISION, "decision_id")
    if before != json.dumps(reviews, ensure_ascii=False, sort_keys=True):
        _write(reviews_path, reviews)
        changed = True
    return changed


def main() -> int:
    print(f"talent_bloom_system_hardening_changed={str(harden(ROOT)).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FINDING_ID = "cf-2672ecdef6c16856"
SOURCE = "中山赛马娘锦标"
SOURCE_JA = "中山ウマ娘S"
TARGET = "Nakayama Uma Musume Stakes"
TERM_ID = "race.nakayama_uma_musume_stakes"
LEGACY_TERM_ID = "race.nakayama_himba_stakes"
DECISION_ID = "audit.finding.nakayama-uma-musume-stakes"

COMMUNITY_RULE = {
    "id": TERM_ID,
    "category": "race",
    "source_aliases": [SOURCE],
    "preferred": TARGET,
    "compact": [],
    "accepted": [TARGET],
    "forbidden": ["Nakayama Himba Stakes"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [],
    "match_mode": "exact",
    "basis": (
        "Pinned in-game race 32/3020 and display 33/3020 are JP 中山ウマ娘S, not real-racing 中山牝馬S. "
        "The project already canonizes the reusable ウマ娘ステークス component as Uma Musume Stakes, "
        "so the full player-facing identity is Nakayama Uma Musume Stakes."
    ),
}

DECISION = {
    "decision_id": DECISION_ID,
    "source_zh_cn": SOURCE,
    "action": "lock",
    "target_vi": TARGET,
    "kind": "race_name",
    "category": "race",
    "ja": [SOURCE_JA],
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [],
    "match_mode": "exact",
    "note": (
        "Supersedes the older defer and the incorrect real-race Himba lock. Pinned JP identity is 中山ウマ娘S; "
        "use the established project component Uma Musume Stakes rather than restoring real-world 牝馬 terminology."
    ),
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
    rid = str(record[id_field])
    for i, item in enumerate(items):
        if isinstance(item, dict) and str(item.get(id_field) or "") == rid:
            merged = dict(item)
            merged.update(record)
            items[i] = merged
            return
    items.append(dict(record))


def harden(repo_root: Path = ROOT) -> bool:
    changed = False

    registry_path = repo_root / "glossary" / "term_registry.json"
    registry = _load(registry_path, {"terms": []})
    before = json.dumps(registry, ensure_ascii=False, sort_keys=True)
    legacy = next(
        (item for item in registry.setdefault("terms", []) if isinstance(item, dict) and item.get("id") == LEGACY_TERM_ID),
        None,
    )
    if legacy is None:
        raise ValueError(f"missing legacy race term {LEGACY_TERM_ID}")
    legacy.update({
        "ja": [SOURCE_JA],
        "zh_cn": [SOURCE],
        "target_vi": TARGET,
        "locked": True,
        "source_paths": ["text_data_dict.json"],
        "json_path_prefixes": [["32"], ["33"], ["111"]],
        "match_mode": "contains",
        "invalidation_scope": "item",
        "note": (
            "Legacy id retained for compatibility, but identity corrected to the in-game JP race 中山ウマ娘S. "
            "Do not map this title back to the real-world 中山牝馬S / Nakayama Himba Stakes."
        ),
    })
    if before != json.dumps(registry, ensure_ascii=False, sort_keys=True):
        _write(registry_path, registry)
        changed = True

    community_path = repo_root / "glossary" / "ui_community_terms.json"
    community = _load(community_path, {"schema_version": 1, "terms": []})
    before = json.dumps(community, ensure_ascii=False, sort_keys=True)
    _upsert(community.setdefault("terms", []), COMMUNITY_RULE, "id")
    if before != json.dumps(community, ensure_ascii=False, sort_keys=True):
        _write(community_path, community)
        changed = True

    reviews_path = repo_root / "glossary" / "terminology_reviews.json"
    reviews = _load(reviews_path, {"schema_version": 1, "decisions": []})
    before = json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    decisions = reviews.setdefault("decisions", [])
    decisions[:] = [
        item for item in decisions
        if not (isinstance(item, dict) and str(item.get("source_zh_cn") or "").strip() == SOURCE and item.get("decision_id") != DECISION_ID)
    ]
    _upsert(decisions, DECISION, "decision_id")
    own = next(item for item in decisions if isinstance(item, dict) and item.get("decision_id") == DECISION_ID)
    decisions.remove(own)
    decisions.append(own)
    if before != json.dumps(reviews, ensure_ascii=False, sort_keys=True):
        _write(reviews_path, reviews)
        changed = True

    findings_path = repo_root / "glossary" / "canonical_findings.json"
    findings = _load(findings_path, {"schema_version": 1, "findings": []})
    before = json.dumps(findings, ensure_ascii=False, sort_keys=True)
    matched = False
    for finding in findings.get("findings", []):
        if isinstance(finding, dict) and finding.get("finding_id") == FINDING_ID:
            matched = True
            suggestions = [str(x) for x in finding.get("suggested_targets_vi", []) if str(x)]
            if TARGET not in suggestions:
                suggestions.append(TARGET)
            finding["suggested_targets_vi"] = suggestions
            break
    if not matched:
        raise ValueError(f"missing canonical finding {FINDING_ID}")
    if before != json.dumps(findings, ensure_ascii=False, sort_keys=True):
        _write(findings_path, findings)
        changed = True

    return changed


def main() -> int:
    changed = harden(ROOT)
    print(f"nakayama_uma_musume_stakes_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

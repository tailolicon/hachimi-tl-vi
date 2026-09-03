from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FINDING_ID = "cf-0e557eef086006fc"
SOURCE = "笑っちゃお！"
TARGET = "Waracchao!"

RULE = {
    "id": "song.waracchao",
    "category": "song",
    "source_aliases": [SOURCE],
    "preferred": TARGET,
    "compact": [],
    "accepted": [TARGET],
    "forbidden": [SOURCE, "Cùng cười nào!"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [["16"]],
    "match_mode": "exact",
    "basis": (
        "Named Daitaku Helios solo song 笑っちゃお！ from UMAMUSUME PRETTY DERBY "
        "WINNING LIVE 08. Preserve the defensible Romanized identity Waracchao! "
        "instead of inventing a semantic Vietnamese proper title."
    ),
}

DECISION = {
    "decision_id": "audit.finding.song-waracchao",
    "source_zh_cn": SOURCE,
    "action": "lock",
    "target_vi": TARGET,
    "kind": "proper_name",
    "category": "song",
    "note": (
        "The source is Daitaku Helios's named solo song. Lock the Romanized identity "
        "Waracchao! rather than the semantic calque Cùng cười nào!."
    ),
}


def _load(path: Path, default: dict[str, Any] | None = None) -> dict[str, Any]:
    if not path.exists():
        return dict(default or {})
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


def _upsert(items: list[Any], record: dict[str, Any], *, id_field: str) -> None:
    record_id = str(record[id_field])
    for index, item in enumerate(items):
        if isinstance(item, dict) and str(item.get(id_field) or "") == record_id:
            merged = dict(item)
            merged.update(record)
            items[index] = merged
            return
    items.append(dict(record))


def _repair_live_finding_scope(repo_root: Path) -> bool:
    ledger_path = repo_root / "glossary" / "canonical_findings.json"
    if not ledger_path.exists():
        return False
    ledger = _load(ledger_path, {"schema_version": 1, "findings": []})
    findings = ledger.get("findings", [])
    if not isinstance(findings, list):
        raise ValueError("glossary/canonical_findings.json findings must be a list")

    changed = False
    for finding in findings:
        if not isinstance(finding, dict):
            continue
        if str(finding.get("finding_id") or "") != FINDING_ID:
            continue
        if str(finding.get("source_zh_cn") or "") != SOURCE:
            continue
        if finding.get("source_paths") != ["text_data_dict.json"]:
            continue
        if finding.get("json_path_prefixes"):
            continue
        evidence = [item for item in finding.get("evidence", []) if isinstance(item, dict)]
        if not evidence:
            continue
        if not all(
            item.get("source_path") == "text_data_dict.json"
            and isinstance(item.get("json_path"), list)
            and item["json_path"]
            and str(item["json_path"][0]) == "16"
            for item in evidence
        ):
            continue
        finding["json_path_prefixes"] = [["16"]]
        changed = True

    if changed:
        _write(ledger_path, ledger)
    return changed


def harden(repo_root: Path = ROOT) -> bool:
    changed = _repair_live_finding_scope(repo_root)

    community_path = repo_root / "glossary" / "ui_community_terms.json"
    community = _load(community_path, {"schema_version": 1, "terms": []})
    terms = community.setdefault("terms", [])
    if not isinstance(terms, list):
        raise ValueError("glossary/ui_community_terms.json terms must be a list")
    before = json.dumps(community, ensure_ascii=False, sort_keys=True)
    _upsert(terms, RULE, id_field="id")
    if before != json.dumps(community, ensure_ascii=False, sort_keys=True):
        _write(community_path, community)
        changed = True

    reviews_path = repo_root / "glossary" / "terminology_reviews.json"
    reviews = _load(reviews_path, {"schema_version": 1, "decisions": []})
    decisions = reviews.setdefault("decisions", [])
    if not isinstance(decisions, list):
        raise ValueError("glossary/terminology_reviews.json decisions must be a list")
    before = json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    _upsert(decisions, DECISION, id_field="decision_id")
    if before != json.dumps(reviews, ensure_ascii=False, sort_keys=True):
        _write(reviews_path, reviews)
        changed = True
    return changed


def main() -> int:
    changed = harden(ROOT)
    print(f"waracchao_song_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

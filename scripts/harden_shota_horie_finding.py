from __future__ import annotations

"""Canonicalize creator credit 堀江晶太 to Sony Music's verified Latin spelling Shota Horie."""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "堀江晶太"
PREFERRED = "Shota Horie"
TERM_ID = "proper_name.shota_horie"

TERM = {
    "id": TERM_ID,
    "category": "proper_name",
    "source_aliases": [SOURCE],
    "preferred": PREFERRED,
    "compact": [],
    "accepted": [PREFERRED],
    "forbidden": [SOURCE],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "match_mode": "contains",
    "basis": (
        "Sony Music's official PENGUIN RESEARCH profile maps 堀江晶太 to SHOTA HORIE, while Lantis' official "
        "Umamusume WINNING LIVE 09 credits 堀江晶太 as composer/arranger of Ms. VICTORIA. Use Shota Horie in release credits."
    ),
}

DECISION = {
    "decision_id": "audit.finding.shota-horie-credit",
    "source_zh_cn": SOURCE,
    "action": "lock",
    "target_vi": PREFERRED,
    "kind": "proper_name",
    "category": "proper_name",
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "match_mode": "contains",
    "note": "Verified creator spelling from Sony Music plus official Lantis Umamusume credits: 堀江晶太 -> Shota Horie.",
}


def _load(path: Path, default: dict[str, Any] | None = None) -> dict[str, Any]:
    if not path.exists(): return dict(default or {})
    payload=json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload,dict): raise ValueError(f"{path} must contain a JSON object")
    return payload


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")


def _upsert(items: list[Any], record: dict[str, Any], *, id_field: str) -> None:
    rid=str(record[id_field])
    for i,item in enumerate(items):
        if isinstance(item,dict) and str(item.get(id_field) or "")==rid:
            merged=dict(item); merged.update(record); items[i]=merged; return
    items.append(dict(record))


def harden(repo_root: Path = ROOT) -> bool:
    changed=False
    community_path=repo_root/"glossary"/"ui_community_terms.json"
    community=_load(community_path,{"schema_version":1,"terms":[]}); terms=community.setdefault("terms",[])
    before=json.dumps(community,ensure_ascii=False,sort_keys=True); _upsert(terms,TERM,id_field="id")
    if before!=json.dumps(community,ensure_ascii=False,sort_keys=True): _write(community_path,community); changed=True
    reviews_path=repo_root/"glossary"/"terminology_reviews.json"
    reviews=_load(reviews_path,{"schema_version":1,"decisions":[]}); decisions=reviews.setdefault("decisions",[])
    before=json.dumps(reviews,ensure_ascii=False,sort_keys=True); _upsert(decisions,DECISION,id_field="decision_id")
    if before!=json.dumps(reviews,ensure_ascii=False,sort_keys=True): _write(reviews_path,reviews); changed=True
    return changed


def main() -> int:
    changed=harden(ROOT); print(f"shota_horie_hardening_changed={str(changed).lower()}"); return 0

if __name__ == "__main__": raise SystemExit(main())

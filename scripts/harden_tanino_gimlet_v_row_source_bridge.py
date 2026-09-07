from __future__ import annotations

"""Resolve the mixed-script Tanino Gimlet profile bridge around ヴ行."""

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "神话、哲学、Vu行的发音、业余木工"
TARGET = "Thần thoại, triết học, phát âm các âm V, làm đồ gỗ DIY"
TERM_ID = "source_bridge.tanino_gimlet.v_row_profile"

RULE = {
    "id": TERM_ID,
    "category": "source_bridge",
    "zh_cn": [SOURCE],
    "preferred": TARGET,
    "compact": [],
    "accepted": [TARGET],
    "forbidden": ["Thần thoại, triết học, phát âm hàng Vu, nghề mộc nghiệp dư"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [["164", "1084"]],
    "match_mode": "exact",
    "basis": (
        "Tanino Gimlet's JP profile lists 神話、哲学、ヴ行の発音、日曜大工. The zh-CN bridge "
        "corrupted ヴ行 into mixed-script Vu行. Here ヴ行 means the Japanese V-series sounds, "
        "not a literal 'Vu row'; 日曜大工 is hobbyist DIY woodworking. Keep this correction scoped "
        "to the exact profile item."
    ),
}

DECISION = {
    "decision_id": "audit.finding.tanino-gimlet-v-row-source-bridge",
    "source_zh_cn": SOURCE,
    "action": "lock",
    "target_vi": TARGET,
    "kind": "source_bridge",
    "category": "source_bridge",
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [["164", "1084"]],
    "match_mode": "exact",
    "note": (
        "Whole-item bridge for Tanino Gimlet's strengths profile. JP source is 神話、哲学、ヴ行の発音、日曜大工; "
        "resolve mixed-script Vu行 as the V-series pronunciation and keep the mapping exact-item scoped."
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


def _upsert(rows: list[Any], record: dict[str, Any], id_field: str) -> None:
    record_id = str(record[id_field])
    for index, row in enumerate(rows):
        if isinstance(row, dict) and str(row.get(id_field) or "") == record_id:
            merged = dict(row)
            merged.pop("source_aliases", None)
            merged.update(record)
            rows[index] = merged
            return
    rows.append(dict(record))


def harden(repo_root: Path = ROOT) -> bool:
    changed = False
    bridge_path = repo_root / "glossary" / "source_bridge_terms.json"
    bridge = _load(bridge_path, {"schema_version": 1, "policy": {}, "terms": [], "untrusted_sources": []})
    before = json.dumps(bridge, ensure_ascii=False, sort_keys=True)
    _upsert(bridge.setdefault("terms", []), RULE, "id")
    if before != json.dumps(bridge, ensure_ascii=False, sort_keys=True):
        _write(bridge_path, bridge)
        changed = True

    reviews_path = repo_root / "glossary" / "terminology_reviews.json"
    reviews = _load(reviews_path, {"schema_version": 1, "decisions": []})
    before = json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    _upsert(reviews.setdefault("decisions", []), DECISION, "decision_id")
    if before != json.dumps(reviews, ensure_ascii=False, sort_keys=True):
        _write(reviews_path, reviews)
        changed = True
    return changed


def main() -> int:
    changed = harden(ROOT)
    print(f"tanino_gimlet_v_row_source_bridge_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

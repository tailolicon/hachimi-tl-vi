from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]


def _load(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _upsert(items: list[dict[str, Any]], record: dict[str, Any]) -> None:
    rid = str(record["id"])
    for index, item in enumerate(items):
        if isinstance(item, dict) and str(item.get("id", "")) == rid:
            merged = dict(item)
            merged.update(record)
            items[index] = merged
            return
    items.append(dict(record))


def harden(repo_root: Path = REPO_ROOT) -> None:
    community_path = repo_root / "glossary/ui_community_terms.json"
    community = _load(community_path, {"terms": []})
    terms = community.setdefault("terms", [])

    records = [
        {
            "id": "common_ui.close.common0007",
            "source_aliases": ["关闭"],
            "preferred": "Đóng",
            "accepted": ["Đóng"],
            "compact": ["Đóng"],
            "forbidden": [],
            "require_accepted": True,
            "source_paths": ["localize_dict.json"],
            "key_exact": ["Common0007"],
            "match_mode": "exact",
            "invalidation_scope": "item",
            "basis": "Common0007 is the generic close control. Exact-key scope avoids matching narrative uses of close/closed.",
        },
        {
            "id": "common_ui.change.common0008",
            "source_aliases": ["更改"],
            "preferred": "Thay đổi",
            "accepted": ["Thay đổi"],
            "compact": ["Đổi"],
            "forbidden": [],
            "require_accepted": True,
            "source_paths": ["localize_dict.json"],
            "key_exact": ["Common0008"],
            "match_mode": "exact",
            "invalidation_scope": "item",
            "basis": "Common0008 is the generic Change control. Keep the roomy label Thay đổi and allow compact Đổi only for width-constrained UI.",
        },
        {
            "id": "common_ui.confirm.common0009",
            "source_aliases": ["确认"],
            "preferred": "Xác nhận",
            "accepted": ["Xác nhận"],
            "compact": ["Xác nhận"],
            "forbidden": [],
            "require_accepted": True,
            "source_paths": ["localize_dict.json"],
            "key_exact": ["Common0009"],
            "match_mode": "exact",
            "invalidation_scope": "item",
            "basis": "Common0009 is the generic Confirm control. Exact-key scope prevents confirmation prose from being treated as a fixed control label.",
        },
        {
            "id": "common_ui.cancel.circle0086",
            "source_aliases": ["取消"],
            "preferred": "Hủy",
            "accepted": ["Hủy"],
            "compact": ["Hủy"],
            "forbidden": [],
            "require_accepted": True,
            "source_paths": ["localize_dict.json"],
            "key_exact": ["Circle0086"],
            "match_mode": "exact",
            "invalidation_scope": "item",
            "basis": "Circle0086 is a standalone Cancel control in the club UI. Exact-key scope excludes prose such as an application having been cancelled.",
        },
        {
            "id": "common_ui.sort.common0087",
            "source_aliases": ["排序"],
            "preferred": "Sắp xếp",
            "accepted": ["Sắp xếp"],
            "compact": ["Sắp xếp"],
            "forbidden": [],
            "require_accepted": True,
            "source_paths": ["localize_dict.json"],
            "key_exact": ["Common0087"],
            "match_mode": "exact",
            "invalidation_scope": "item",
            "basis": "Common0087 is the generic Sort control. Exact-key scope prevents ordinary ordering prose from matching.",
        },
        {
            "id": "common_ui.filter.common0098",
            "source_aliases": ["筛选"],
            "preferred": "Lọc",
            "accepted": ["Lọc"],
            "compact": ["Lọc"],
            "forbidden": [],
            "require_accepted": True,
            "source_paths": ["localize_dict.json"],
            "key_exact": ["Common0098"],
            "match_mode": "exact",
            "invalidation_scope": "item",
            "basis": "Common0098 is the generic Filter control. Exact-key scope prevents narrative filtering/selecting language from matching.",
        },
    ]
    for record in records:
        _upsert(terms, record)
    _write(community_path, community)


if __name__ == "__main__":
    harden()

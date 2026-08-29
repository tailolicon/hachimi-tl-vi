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

    invalid_ids = {"common_ui.on.common0092", "common_ui.off.common0093"}
    terms[:] = [item for item in terms if not isinstance(item, dict) or str(item.get("id", "")) not in invalid_ids]

    records = [
        {"id": "common_ui.confirm.common0001", "source_aliases": ["确定"], "preferred": "Xác nhận", "accepted": ["Xác nhận"], "compact": ["Xác nhận"], "forbidden": [], "require_accepted": True, "source_paths": ["localize_dict.json"], "key_exact": ["Common0001"], "match_mode": "exact", "invalidation_scope": "item", "basis": "Common0001 is the primary generic Confirm control. Exact-key scope prevents the broad source verb from forcing prose."},
        {"id": "common_ui.cancel.common0002_0004", "source_aliases": ["取消"], "preferred": "Hủy", "accepted": ["Hủy"], "compact": ["Hủy"], "forbidden": [], "require_accepted": True, "source_paths": ["localize_dict.json"], "key_exact": ["Common0002", "Common0004"], "match_mode": "exact", "invalidation_scope": "item", "basis": "Common0002 and Common0004 are generic Cancel controls. Exact-key scope excludes cancelled-status prose and action-specific compounds."},
        {"id": "common_ui.selecting.common0005", "source_aliases": ["选择中"], "preferred": "Đang chọn", "accepted": ["Đang chọn"], "compact": ["Đang chọn"], "forbidden": [], "require_accepted": True, "source_paths": ["localize_dict.json"], "key_exact": ["Common0005"], "match_mode": "exact", "invalidation_scope": "item", "basis": "Common0005 is the generic Selecting status. Exact-key scope avoids treating selection prose as a fixed label."},
        {"id": "common_ui.close.common0007", "source_aliases": ["关闭"], "preferred": "Đóng", "accepted": ["Đóng"], "compact": ["Đóng"], "forbidden": [], "require_accepted": True, "source_paths": ["localize_dict.json"], "key_exact": ["Common0007"], "match_mode": "exact", "invalidation_scope": "item", "basis": "Common0007 is the generic Close control. Exact-key scope prevents this generic source token from leaking into unrelated contexts."},
        {"id": "common_ui.change.common0008", "source_aliases": ["更改"], "preferred": "Thay đổi", "accepted": ["Thay đổi"], "compact": ["Đổi"], "forbidden": [], "require_accepted": True, "source_paths": ["localize_dict.json"], "key_exact": ["Common0008"], "match_mode": "exact", "invalidation_scope": "item", "basis": "Common0008 is the generic Change control. Keep the roomy label Thay đổi and allow compact Đổi only for width-constrained UI."},
        {"id": "common_ui.confirm.common0009", "source_aliases": ["确认"], "preferred": "Xác nhận", "accepted": ["Xác nhận"], "compact": ["Xác nhận"], "forbidden": [], "require_accepted": True, "source_paths": ["localize_dict.json"], "key_exact": ["Common0009"], "match_mode": "exact", "invalidation_scope": "item", "basis": "Common0009 is the generic Confirm control. Exact-key scope prevents confirmation prose from being treated as a fixed control label."},
        {"id": "common_ui.use.common0013", "source_aliases": ["使用"], "preferred": "Sử dụng", "accepted": ["Sử dụng"], "compact": ["Dùng"], "forbidden": [], "require_accepted": True, "source_paths": ["localize_dict.json"], "key_exact": ["Common0013"], "match_mode": "exact", "invalidation_scope": "item", "basis": "Common0013 is a generic Use control. Exact-key scope keeps ordinary prose about using an item outside this canonical UI rule."},
        {"id": "common_ui.cancel.circle0086", "source_aliases": ["取消"], "preferred": "Hủy", "accepted": ["Hủy"], "compact": ["Hủy"], "forbidden": [], "require_accepted": True, "source_paths": ["localize_dict.json"], "key_exact": ["Circle0086"], "match_mode": "exact", "invalidation_scope": "item", "basis": "Circle0086 is a standalone Cancel control in the club UI. Exact-key scope excludes prose such as an application having been cancelled."},
        {"id": "common_ui.back.common0082", "source_aliases": ["返回"], "preferred": "Quay lại", "accepted": ["Quay lại"], "compact": ["Quay lại"], "forbidden": [], "require_accepted": True, "source_paths": ["localize_dict.json"], "key_exact": ["Common0082"], "match_mode": "exact", "invalidation_scope": "item", "basis": "Common0082 is the generic Back control. Exact-key scope excludes narrative return wording and longer destination-specific labels."},
        {"id": "common_ui.next.common0083", "source_aliases": ["下项"], "preferred": "Tiếp theo", "accepted": ["Tiếp theo"], "compact": ["Tiếp theo"], "forbidden": [], "require_accepted": True, "source_paths": ["localize_dict.json"], "key_exact": ["Common0083"], "match_mode": "exact", "invalidation_scope": "item", "basis": "Common0083 is the generic Next control in the Common label group; key scope avoids assuming the uncommon bridge token is globally equivalent to next."},
        {"id": "common_ui.remove.common0084", "source_aliases": ["卸下"], "preferred": "Tháo", "accepted": ["Tháo"], "compact": ["Tháo"], "forbidden": [], "require_accepted": True, "source_paths": ["localize_dict.json"], "key_exact": ["Common0084"], "match_mode": "exact", "invalidation_scope": "item", "basis": "Common0084 is a compact generic Remove/Unequip control. Exact-key scope prevents equipment/action prose from being flattened into a global rule."},
        {"id": "common_ui.unspecified.common0085", "source_aliases": ["无指定"], "preferred": "Không chỉ định", "accepted": ["Không chỉ định"], "compact": ["Không chỉ định"], "forbidden": [], "require_accepted": True, "source_paths": ["localize_dict.json"], "key_exact": ["Common0085"], "match_mode": "exact", "invalidation_scope": "item", "basis": "Common0085 is the generic Unspecified filter/selection state. Exact-key scope avoids imposing it on prose."},
        {"id": "common_ui.sort.common0087", "source_aliases": ["排序"], "preferred": "Sắp xếp", "accepted": ["Sắp xếp"], "compact": ["Sắp xếp"], "forbidden": [], "require_accepted": True, "source_paths": ["localize_dict.json"], "key_exact": ["Common0087"], "match_mode": "exact", "invalidation_scope": "item", "basis": "Common0087 is the generic Sort control. Exact-key scope prevents ordinary ordering prose from matching."},
        {"id": "common_ui.reset.common0096", "source_aliases": ["重置"], "preferred": "Đặt lại", "accepted": ["Đặt lại"], "compact": ["Đặt lại"], "forbidden": [], "require_accepted": True, "source_paths": ["localize_dict.json"], "key_exact": ["Common0096"], "match_mode": "exact", "invalidation_scope": "item", "basis": "Common0096 is the generic Reset control. Exact-key scope avoids treating reset/restart prose as a fixed UI label."},
        {"id": "common_ui.cannot_select.common0097", "source_aliases": ["不能选择"], "preferred": "Không thể chọn", "accepted": ["Không thể chọn"], "compact": ["Không thể chọn"], "forbidden": [], "require_accepted": True, "source_paths": ["localize_dict.json"], "key_exact": ["Common0097"], "match_mode": "exact", "invalidation_scope": "item", "basis": "Common0097 is the generic Cannot select state. Exact-key scope prevents ordinary inability-to-select prose from becoming a fixed label."},
        {"id": "common_ui.filter.common0098", "source_aliases": ["筛选"], "preferred": "Lọc", "accepted": ["Lọc"], "compact": ["Lọc"], "forbidden": [], "require_accepted": True, "source_paths": ["localize_dict.json"], "key_exact": ["Common0098"], "match_mode": "exact", "invalidation_scope": "item", "basis": "Common0098 is the generic Filter control. Exact-key scope prevents narrative filtering/selecting language from matching."},
        {"id": "common_ui.sort_ascending.common0100", "source_aliases": ["升序"], "preferred": "Tăng dần", "accepted": ["Tăng dần"], "compact": ["Tăng dần"], "forbidden": [], "require_accepted": True, "source_paths": ["localize_dict.json"], "key_exact": ["Common0100"], "match_mode": "exact", "invalidation_scope": "item", "basis": "Common0100 is the generic ascending sort-order label and is scoped to the Common UI key."},
        {"id": "common_ui.sort_descending.common0101", "source_aliases": ["降序"], "preferred": "Giảm dần", "accepted": ["Giảm dần"], "compact": ["Giảm dần"], "forbidden": [], "require_accepted": True, "source_paths": ["localize_dict.json"], "key_exact": ["Common0101"], "match_mode": "exact", "invalidation_scope": "item", "basis": "Common0101 is the generic descending sort-order label and is scoped to the Common UI key."},
        {"id": "common_ui.display_order.common0136", "source_aliases": ["显示顺序"], "preferred": "Thứ tự hiển thị", "accepted": ["Thứ tự hiển thị"], "compact": ["Thứ tự hiển thị"], "forbidden": [], "require_accepted": True, "source_paths": ["localize_dict.json"], "key_exact": ["Common0136"], "match_mode": "exact", "invalidation_scope": "item", "basis": "Common0136 is the generic Display order label. Exact-key scope avoids broad ordering aliases."},
        {"id": "common_ui.details.roommatch0117", "source_aliases": ["详情"], "preferred": "Chi tiết", "accepted": ["Chi tiết"], "compact": ["Chi tiết"], "forbidden": [], "require_accepted": True, "source_paths": ["localize_dict.json"], "key_exact": ["RoomMatch0117"], "match_mode": "exact", "invalidation_scope": "item", "basis": "RoomMatch0117 is a standalone Details control. Exact-key scope avoids matching the same source word inside compound detail headings."},
    ]
    for record in records:
        _upsert(terms, record)
    _write(community_path, community)


if __name__ == "__main__":
    harden()

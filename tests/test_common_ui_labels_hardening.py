from __future__ import annotations

import json
from pathlib import Path

from scripts.harden_common_ui_labels import harden
from scripts.translation_review_common import community_term_matches, load_community_terms


def _write(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _seed(tmp_path: Path) -> Path:
    glossary = tmp_path / "glossary"
    _write(glossary / "ui_community_terms.json", {"terms": []})
    harden(tmp_path)
    return tmp_path


def _record(root: Path, key: str, source: str, target: str, rid: str):
    matches = community_term_matches(key, source, target, load_community_terms(root), source_path="localize_dict.json", json_path=[key])
    return next(item for item in matches if item["id"] == rid)


def test_common_status_and_action_controls_are_exact_key_scoped(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    cases = [
        ("Common0005", "选择中", "Đang chọn", "common_ui.selecting.common0005"),
        ("Common0007", "关闭", "Đóng", "common_ui.close.common0007"),
        ("Common0008", "更改", "Thay đổi", "common_ui.change.common0008"),
        ("Common0009", "确认", "Xác nhận", "common_ui.confirm.common0009"),
        ("Common0013", "使用", "Sử dụng", "common_ui.use.common0013"),
    ]
    for key, source, target, rid in cases:
        record = _record(root, key, source, target, rid)
        assert record["accepted_present"] is True
        assert record["forbidden_present"] is False
        assert community_term_matches(None, source, target, load_community_terms(root), source_path="story.json", json_path=["1"]) == []


def test_compact_control_forms_are_accepted(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    assert _record(root, "Common0008", "更改", "Đổi", "common_ui.change.common0008")["accepted_present"] is True
    assert _record(root, "Common0013", "使用", "Dùng", "common_ui.use.common0013")["accepted_present"] is True


def test_cancel_is_scoped_to_standalone_circle_control(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    assert _record(root, "Circle0086", "取消", "Hủy", "common_ui.cancel.circle0086")["accepted_present"] is True
    assert community_term_matches("Circle0085", "申请已取消", "Đã hủy đăng ký", load_community_terms(root), source_path="localize_dict.json", json_path=["Circle0085"]) == []
    assert community_term_matches("RoomMatch0124", "取消举办", "Hủy tổ chức", load_community_terms(root), source_path="localize_dict.json", json_path=["RoomMatch0124"]) == []


def test_navigation_and_sort_controls_are_exact_key_scoped(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    cases = [
        ("Common0082", "返回", "Quay lại", "common_ui.back.common0082"),
        ("Common0083", "下项", "Tiếp theo", "common_ui.next.common0083"),
        ("Common0084", "卸下", "Tháo", "common_ui.remove.common0084"),
        ("Common0087", "排序", "Sắp xếp", "common_ui.sort.common0087"),
        ("Common0096", "重置", "Đặt lại", "common_ui.reset.common0096"),
        ("Common0098", "筛选", "Lọc", "common_ui.filter.common0098"),
        ("Common0100", "升序", "Tăng dần", "common_ui.sort_ascending.common0100"),
        ("Common0101", "降序", "Giảm dần", "common_ui.sort_descending.common0101"),
    ]
    for key, source, target, rid in cases:
        record = _record(root, key, source, target, rid)
        assert record["accepted_present"] is True
        assert record["forbidden_present"] is False
        assert community_term_matches(None, source, target, load_community_terms(root), source_path="story.json", json_path=["1"]) == []


def test_hardener_removes_invalid_toggle_rules_for_race_phase_keys(tmp_path: Path) -> None:
    glossary = tmp_path / "glossary"
    _write(glossary / "ui_community_terms.json", {"terms": [
        {"id": "common_ui.on.common0092", "source_aliases": ["开启"], "preferred": "Bật"},
        {"id": "common_ui.off.common0093", "source_aliases": ["关闭"], "preferred": "Tắt"},
    ]})
    harden(tmp_path)
    ids = {str(item.get("id")) for item in json.loads((glossary / "ui_community_terms.json").read_text(encoding="utf-8"))["terms"]}
    assert "common_ui.on.common0092" not in ids
    assert "common_ui.off.common0093" not in ids
    assert community_term_matches("Common0092", "中盘", "Giữa cuộc đua", load_community_terms(tmp_path), source_path="localize_dict.json", json_path=["Common0092"]) == []
    assert community_term_matches("Common0093", "终盘", "Cuối cuộc đua", load_community_terms(tmp_path), source_path="localize_dict.json", json_path=["Common0093"]) == []


def test_details_is_scoped_to_standalone_roommatch_control(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    assert _record(root, "RoomMatch0117", "详情", "Chi tiết", "common_ui.details.roommatch0117")["accepted_present"] is True
    assert community_term_matches("Outgame0167", "支援卡详情", "Chi tiết Support Card", load_community_terms(root), source_path="localize_dict.json", json_path=["Outgame0167"]) == []


def test_common_ui_hardener_is_idempotent(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    path = root / "glossary/ui_community_terms.json"
    before = path.read_text(encoding="utf-8")
    harden(root)
    assert path.read_text(encoding="utf-8") == before

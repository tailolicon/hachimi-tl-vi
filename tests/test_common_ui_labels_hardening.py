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
    matches = community_term_matches(
        key,
        source,
        target,
        load_community_terms(root),
        source_path="localize_dict.json",
        json_path=[key],
    )
    return next(item for item in matches if item["id"] == rid)


def test_close_change_confirm_controls_are_exact_key_scoped(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    cases = [
        ("Common0007", "关闭", "Đóng", "common_ui.close.common0007"),
        ("Common0008", "更改", "Thay đổi", "common_ui.change.common0008"),
        ("Common0009", "确认", "Xác nhận", "common_ui.confirm.common0009"),
    ]
    for key, source, target, rid in cases:
        record = _record(root, key, source, target, rid)
        assert record["accepted_present"] is True
        assert record["forbidden_present"] is False
        assert community_term_matches(
            None,
            source,
            target,
            load_community_terms(root),
            source_path="story.json",
            json_path=["1"],
        ) == []


def test_change_allows_compact_control_form(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    record = _record(root, "Common0008", "更改", "Đổi", "common_ui.change.common0008")
    assert record["accepted_present"] is True


def test_cancel_is_scoped_to_standalone_circle_control(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    record = _record(root, "Circle0086", "取消", "Hủy", "common_ui.cancel.circle0086")
    assert record["accepted_present"] is True
    assert community_term_matches(
        "Circle0085",
        "申请已取消",
        "Đã hủy đăng ký",
        load_community_terms(root),
        source_path="localize_dict.json",
        json_path=["Circle0085"],
    ) == []


def test_common_ui_hardener_is_idempotent(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    path = root / "glossary/ui_community_terms.json"
    before = path.read_text(encoding="utf-8")
    harden(root)
    assert path.read_text(encoding="utf-8") == before

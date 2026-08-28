from __future__ import annotations

import json
from pathlib import Path

from hachimi_tl_vi.translation_guard import TranslationQualityGuard


def _write(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")


def _guard(tmp_path: Path) -> TranslationQualityGuard:
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    _write(
        glossary / "term_registry.json",
        {
            "terms": [
                {"id": "legacy.speed", "locked": True, "zh_cn": ["速度"], "target_vi": "Tốc độ"},
                {"id": "locked.foo", "locked": True, "zh_cn": ["术语"], "target_vi": "Chuẩn"},
            ]
        },
    )
    _write(
        glossary / "ui_community_terms.json",
        {
            "terms": [
                {
                    "id": "common.speed",
                    "source_aliases": ["速度"],
                    "accepted": ["Speed"],
                    "compact": [],
                    "forbidden": ["Tốc độ"],
                    "require_accepted": True,
                }
            ]
        },
    )
    _write(
        glossary / "skill_name_style.json",
        {"canonical_examples": [{"source_zh_cn": "前行", "target_vi": "Nhắm Hàng Trước"}]},
    )
    _write(
        glossary / "characters.json",
        {
            "characters": {
                "1007": {
                    "identity_status": "verified_game_id",
                    "canonical": "Gold Ship",
                    "zh_cn": ["黄金船"],
                }
            }
        },
    )
    _write(
        glossary / "source_bridge_terms.json",
        {
            "terms": [
                {
                    "id": "currency.monies",
                    "zh_cn": ["金币"],
                    "accepted": ["Monies"],
                    "forbidden": ["xu"],
                    "require_accepted": True,
                }
            ],
            "untrusted_sources": [
                {"id": "bridge.front", "zh_cn_exact": ["前行"], "mode": "defer_until_canonical"},
                {"id": "bridge.lossy", "zh_cn_exact": ["一念胜负"], "mode": "defer_until_canonical"},
            ],
        },
    )
    _write(glossary / "source_bridge_risks.generated.json", {"untrusted_sources": []})
    _write(
        glossary / "translation_regressions.generated.json",
        {
            "entries": [
                {
                    "id": "review.regression.test",
                    "uid": "zhcn:test",
                    "scope": "uid",
                    "source_text": "重新启动",
                    "rejected_targets": ["Khởi chạy lại"],
                    "approved_target": "Khởi động lại",
                }
            ]
        },
    )
    return TranslationQualityGuard(glossary)


def test_player_facing_rule_overrides_old_locked_mapping(tmp_path: Path) -> None:
    guard = _guard(tmp_path)
    assert guard.validate("速度", "Speed") == []
    errors = guard.validate("速度", "Tốc độ")
    assert "community_forbidden:common.speed" in errors
    assert "community_required:common.speed" in errors
    assert not any(error.startswith("locked_term_required:legacy.speed") for error in errors)


def test_locked_term_is_hard_required_when_not_overridden(tmp_path: Path) -> None:
    guard = _guard(tmp_path)
    assert "locked_term_required:locked.foo" in guard.validate("术语说明", "Giải thích")
    assert guard.validate("术语说明", "Giải thích Chuẩn") == []


def test_source_bridge_calque_is_blocked(tmp_path: Path) -> None:
    guard = _guard(tmp_path)
    errors = guard.validate("金币不足", "Không đủ xu")
    assert "source_bridge_forbidden:currency.monies" in errors
    assert "source_bridge_required:currency.monies" in errors
    assert guard.validate("金币不足", "Không đủ Monies") == []


def test_untrusted_source_blocks_guess_but_exact_canonical_resolves_it(tmp_path: Path) -> None:
    guard = _guard(tmp_path)
    assert any(error.startswith("source_bridge_untrusted:bridge.lossy") for error in guard.validate("一念胜负", "Một Niệm Thắng Bại"))
    assert guard.validate("前行", "Nhắm Hàng Trước") == []
    assert "canonical_skill_title_mismatch" in guard.validate("前行", "Tiến lên")


def test_character_name_cannot_be_literalized(tmp_path: Path) -> None:
    guard = _guard(tmp_path)
    assert "character_name_required:1007" in guard.validate("黄金船来了", "Con tàu vàng tới rồi")
    assert guard.validate("黄金船来了", "Gold Ship tới rồi") == []


def test_reviewed_bad_translation_cannot_recur(tmp_path: Path) -> None:
    guard = _guard(tmp_path)
    errors = guard.validate("重新启动", "Khởi chạy lại", uid="zhcn:test")
    assert "known_bad_regression:review.regression.test" in errors
    assert guard.validate("重新启动", "Khởi động lại", uid="zhcn:test") == []


def test_numeric_semantics_are_hard_preserved(tmp_path: Path) -> None:
    guard = _guard(tmp_path)
    assert "numeric_token_mismatch" in guard.validate("最多60个", "Tối đa 50")
    assert guard.validate("最多60个", "Tối đa 60") == []

from __future__ import annotations

from pathlib import Path

from hachimi_tl_vi.translation_guard import TranslationQualityGuard
from scripts.translation_review_common import community_term_matches, load_community_terms


REPO_ROOT = Path(__file__).resolve().parents[1]


def _guard() -> TranslationQualityGuard:
    return TranslationQualityGuard(REPO_ROOT / "glossary")


def _speed_matches(source: str, target: str, *, key: str | None = None, source_path: str = "text_data_dict.json", json_path: list[str] | None = None):
    matches = community_term_matches(
        key,
        source,
        target,
        load_community_terms(REPO_ROOT),
        source_path=source_path,
        json_path=json_path,
    )
    return [item for item in matches if str(item.get("id", "")).startswith("common.stat.speed")]


def test_standalone_speed_stat_label_requires_speed() -> None:
    guard = _guard()
    errors = guard.validate(
        "速度",
        "Tốc độ",
        key="Common0072",
        source_path="localize_dict.json",
        json_path=["Common0072"],
    )
    assert "community_forbidden:common.stat.speed" in errors
    assert "community_required:common.stat.speed" in errors
    assert guard.validate(
        "速度",
        "Speed",
        key="Common0072",
        source_path="localize_dict.json",
        json_path=["Common0072"],
    ) == []

    matches = _speed_matches(
        "速度",
        "Tốc độ",
        key="Common0072",
        source_path="localize_dict.json",
        json_path=["Common0072"],
    )
    assert [item["id"] for item in matches] == ["common.stat.speed"]
    assert matches[0]["forbidden_present"] is True
    assert matches[0]["accepted_present"] is False


def test_embedded_quoted_speed_stat_requires_speed() -> None:
    source = "短途马S结束后・「速度」"
    bad = "Sau Sprinters Stakes・“Tốc độ”"
    good = "Sau Sprinters Stakes・“Speed”"

    errors = _guard().validate(
        source,
        bad,
        uid="zhcn:cc191aa8a93945f7063baa31",
        source_path="text_data_dict.json",
        json_path=["181", "501010423"],
    )
    assert "community_required:common.stat.speed.context" in errors
    assert _guard().validate(
        source,
        good,
        uid="zhcn:cc191aa8a93945f7063baa31",
        source_path="text_data_dict.json",
        json_path=["181", "501010423"],
    ) == []

    matches = _speed_matches(source, bad, json_path=["181", "501010423"])
    assert [item["id"] for item in matches] == ["common.stat.speed.context"]
    assert matches[0]["accepted_present"] is False


def test_stat_threshold_can_coexist_with_literal_max_speed() -> None:
    source = "当速度超过2000时，在最后冲刺阶段满足条件时\\n最高速度会提升。"
    target = "Khi Speed vượt 2000, nếu đáp ứng điều kiện ở nước rút cuối,\\ntốc độ tối đa sẽ tăng."

    assert _guard().validate(
        source,
        target,
        source_path="text_data_dict.json",
        json_path=["450", "12"],
    ) == []
    matches = _speed_matches(source, target, json_path=["450", "12"])
    assert [item["id"] for item in matches] == ["common.stat.speed.context"]
    assert matches[0]["accepted_present"] is True
    assert matches[0]["forbidden_present"] is False


def test_growth_rate_prose_is_not_forced_to_speed_stat() -> None:
    source = "这种成长速度……灿烂的眼神……"
    target = "Tốc độ trưởng thành này... ánh mắt rực rỡ này..."

    assert _guard().validate(
        source,
        target,
        source_path="text_data_dict.json",
        json_path=["139", "5"],
    ) == []
    assert _speed_matches(source, target, json_path=["139", "5"]) == []


def test_skip_speed_and_max_speed_are_not_stat_aliases() -> None:
    assert _speed_matches(
        "提高跳过速度",
        "Tăng tốc độ bỏ qua",
        source_path="localize_dict.json",
        key="SingleMode423001",
        json_path=["SingleMode423001"],
    ) == []
    assert _speed_matches(
        "最高速度会提升",
        "Tốc độ tối đa sẽ tăng",
        json_path=["450", "99"],
    ) == []

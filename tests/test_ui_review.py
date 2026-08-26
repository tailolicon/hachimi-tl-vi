from scripts.ui_review_common import is_review_candidate, risk_flags, text_fingerprint, visual_width


def test_visual_width_prefers_compact_vietnamese_label():
    assert visual_width("Tủ cúp") < visual_width("Phòng trưng bày cúp")


def test_risk_flags_detect_common_ui_regressions():
    flags = risk_flags("物品/转换", "Vật phẩm/Chuyển đổi")
    assert "slash_compound" in flags
    assert "verbose_wording" in flags


def test_short_changed_localize_is_review_candidate():
    assert is_review_candidate("奖杯陈列室", "Phòng trưng bày cúp") is True


def test_identical_source_is_not_retroactive_translation_candidate():
    assert is_review_candidate("GⅠ", "GⅠ") is False


def test_text_fingerprint_changes_with_reviewed_text():
    assert text_fingerprint("Tủ cúp") != text_fingerprint("Phòng trưng bày cúp")

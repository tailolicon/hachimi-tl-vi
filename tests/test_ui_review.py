from scripts.ui_review_common import is_review_candidate, risk_flags, text_fingerprint, visual_width


def test_visual_width_prefers_compact_vietnamese_label():
    assert visual_width("Tủ cúp") < visual_width("Phòng trưng bày cúp")


def test_risk_flags_detect_common_ui_regressions():
    flags = risk_flags("物品/转换", "Vật phẩm/Chuyển đổi")
    assert "slash_compound" in flags
    assert "verbose_wording" in flags


def test_placeholder_date_slash_is_not_a_slash_compound():
    flags = risk_flags("{0}/{1}", "{0}/{1}")
    assert "slash_compound" not in flags


def test_short_changed_localize_is_review_candidate():
    assert is_review_candidate("奖杯陈列室", "Phòng trưng bày cúp") is True


def test_prose_sentence_is_not_ui_review_candidate():
    assert is_review_candidate("此内容可通过切换按钮随时更改", "Nội dung này có thể thay đổi bất cứ lúc nào bằng nút chuyển") is False
    assert is_review_candidate("请选择项目。", "Hãy chọn mục.") is False


def test_identical_source_is_not_retroactive_translation_candidate():
    assert is_review_candidate("GⅠ", "GⅠ") is False


def test_text_fingerprint_changes_with_reviewed_text():
    assert text_fingerprint("Tủ cúp") != text_fingerprint("Phòng trưng bày cúp")

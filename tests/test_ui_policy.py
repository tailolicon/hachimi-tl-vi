from __future__ import annotations

import json
from pathlib import Path

from hachimi_tl_vi.ui_policy import apply_ui_overrides, assess_compact_ui, visual_units


def test_visual_units_treats_cjk_as_wider_than_latin() -> None:
    assert visual_units("奖杯陈列室") > visual_units("Tủ cúp")


def test_compact_ui_flags_overflow_and_accepts_short_form() -> None:
    bad = assess_compact_ui(
        "奖杯陈列室",
        "Phòng trưng bày cúp",
        kind="localize",
        source_path="localize_dict.json",
    )
    good = assess_compact_ui(
        "奖杯陈列室",
        "Tủ cúp",
        kind="localize",
        source_path="localize_dict.json",
    )
    assert bad["warnings"]
    assert not good["warnings"]


def test_apply_ui_overrides_supports_key_and_exact_replacements(tmp_path: Path) -> None:
    (tmp_path / "glossary").mkdir()
    (tmp_path / "localized_data").mkdir()
    (tmp_path / "glossary" / "ui_overrides.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "key_overrides": [
                    {"file": "localize_dict.json", "path": ["Menu0004"], "text": "Tủ cúp"}
                ],
                "exact_replacements": [
                    {
                        "files": ["localize_dict.json"],
                        "from": "Lịch sử Gacha",
                        "to": "Lịch sử"
                    }
                ]
            },
            ensure_ascii=False
        ),
        encoding="utf-8"
    )
    (tmp_path / "localized_data" / "localize_dict.json").write_text(
        json.dumps(
            {"Menu0004": "Phòng trưng bày cúp", "Other": "Lịch sử Gacha"},
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    report = apply_ui_overrides(tmp_path)
    data = json.loads((tmp_path / "localized_data" / "localize_dict.json").read_text(encoding="utf-8"))

    assert report["total_changes"] == 2
    assert data["Menu0004"] == "Tủ cúp"
    assert data["Other"] == "Lịch sử"

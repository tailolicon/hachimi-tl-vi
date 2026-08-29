from __future__ import annotations

import json
from pathlib import Path

from scripts.harden_training_support_canon import harden
from scripts.translation_review_common import community_term_matches, load_community_terms, load_locked_terms, locked_term_matches


def _write(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _seed(tmp_path: Path) -> Path:
    glossary = tmp_path / "glossary"
    _write(
        glossary / "term_registry.json",
        {
            "terms": [
                {
                    "id": "system.friendship_training",
                    "category": "training",
                    "ja": ["友情トレーニング"],
                    "zh_cn": ["友情训练"],
                    "target_vi": "Huấn luyện Hữu nghị",
                    "locked": True,
                },
                {
                    "id": "progress.bond",
                    "category": "progression",
                    "ja": ["絆"],
                    "zh_cn": ["羁绊"],
                    "target_vi": "Gắn kết",
                    "locked": True,
                },
            ]
        },
    )
    _write(glossary / "ui_community_terms.json", {"terms": []})
    harden(tmp_path)
    return tmp_path


def _ids(items: list[dict[str, object]]) -> set[str]:
    return {str(item.get("id")) for item in items}


def test_friendship_training_uses_player_facing_term(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    locked = load_locked_terms(root)
    community = load_community_terms(root)
    source = "可以与队伍成员进行友情训练"
    target = "Có thể thực hiện Friendship Training với thành viên đội"
    assert "system.friendship_training" in _ids(
        locked_term_matches(source, target, locked, source_path="text_data_dict.json", json_path=["143", "100"])
    )
    assert "common.friendship_training" in _ids(
        community_term_matches(
            None,
            source,
            target,
            community,
            source_path="text_data_dict.json",
            json_path=["143", "100"],
        )
    )


def test_friendship_training_rejects_historical_calques(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    community = load_community_terms(root)
    matches = community_term_matches(
        None,
        "友情训练",
        "Huấn luyện tình bạn",
        community,
        source_path="text_data_dict.json",
        json_path=["143", "100"],
    )
    record = next(item for item in matches if item["id"] == "common.friendship_training")
    assert record["accepted_present"] is False
    assert record["forbidden_present"] is True


def test_bare_friendship_or_training_prose_does_not_match(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    locked = load_locked_terms(root)
    community = load_community_terms(root)
    for source in ("友情加深了", "今天继续训练", "支持朋友的训练"):
        assert "system.friendship_training" not in _ids(
            locked_term_matches(source, "Câu văn tự nhiên", locked, source_path="story.json", json_path=["1"])
        )
        assert "common.friendship_training" not in _ids(
            community_term_matches(None, source, "Câu văn tự nhiên", community, source_path="story.json", json_path=["1"])
        )


def test_support_points_common0160_uses_compact_resource_label(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    locked = load_locked_terms(root)
    community = load_community_terms(root)
    source = "支援点数"
    target = "Support Pt"
    assert "resource.support_points.common0160" in _ids(
        locked_term_matches(source, target, locked, source_path="localize_dict.json", json_path=["Common0160"])
    )
    matches = community_term_matches(
        "Common0160",
        source,
        target,
        community,
        source_path="localize_dict.json",
        json_path=["Common0160"],
    )
    record = next(item for item in matches if item["id"] == "common.support_points.common0160")
    assert record["accepted_present"] is True
    assert record["forbidden_present"] is False


def test_support_points_rule_does_not_match_other_support_prose(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    locked = load_locked_terms(root)
    community = load_community_terms(root)
    source = "支援点数"
    assert "resource.support_points.common0160" not in _ids(
        locked_term_matches(source, "Điểm hỗ trợ", locked, source_path="story.json", json_path=["1"])
    )
    assert community_term_matches(
        None,
        source,
        "Điểm hỗ trợ",
        community,
        source_path="story.json",
        json_path=["1"],
    ) == []


def test_energy_is_enforced_only_for_known_training_ui_slots(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    locked = load_locked_terms(root)
    community = load_community_terms(root)
    source = "体力<color=#2E85E6>减少了{0}</color>"
    target = "Energy<color=#2E85E6>giảm {0}</color>"
    assert "state.energy.singlemode" in _ids(
        locked_term_matches(source, target, locked, source_path="localize_dict.json", json_path=["SingleMode0074"])
    )
    assert "common.energy.singlemode" in _ids(
        community_term_matches(
            "SingleMode0074",
            source,
            target,
            community,
            source_path="localize_dict.json",
            json_path=["SingleMode0074"],
        )
    )
    assert "state.energy.singlemode" not in _ids(
        locked_term_matches("体力をつける", "Rèn thể lực", locked, source_path="story.json", json_path=["1"])
    )
    assert community_term_matches(
        None,
        "体力をつける",
        "Rèn thể lực",
        community,
        source_path="story.json",
        json_path=["1"],
    ) == []


def test_friendship_gauge_replaces_global_bond_calque_in_support_effects(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    locked = load_locked_terms(root)
    community = load_community_terms(root)
    source = "羁绊值在80以上时，速度加成"
    target = "Khi Friendship Gauge đạt 80 trở lên, Speed Bonus"
    locked_matches = locked_term_matches(
        source,
        target,
        locked,
        source_path="text_data_dict.json",
        json_path=["155", "30288"],
    )
    assert "progress.friendship_gauge.support_effects" in _ids(locked_matches)
    assert "progress.bond" not in _ids(locked_matches)
    assert "common.friendship_gauge.support_effects" in _ids(
        community_term_matches(
            None,
            source,
            target,
            community,
            source_path="text_data_dict.json",
            json_path=["155", "30288"],
        )
    )


def test_bare_bond_prose_is_not_forced_to_friendship_gauge(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    locked = load_locked_terms(root)
    community = load_community_terms(root)
    source = "羁绊加深了"
    assert "progress.friendship_gauge.support_effects" not in _ids(
        locked_term_matches(source, "Tình bạn sâu sắc hơn", locked, source_path="story.json", json_path=["1"])
    )
    assert community_term_matches(
        None,
        source,
        "Tình bạn sâu sắc hơn",
        community,
        source_path="story.json",
        json_path=["1"],
    ) == []


def test_hardener_is_idempotent(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    before = (
        (root / "glossary/term_registry.json").read_text(encoding="utf-8"),
        (root / "glossary/ui_community_terms.json").read_text(encoding="utf-8"),
    )
    harden(root)
    after = (
        (root / "glossary/term_registry.json").read_text(encoding="utf-8"),
        (root / "glossary/ui_community_terms.json").read_text(encoding="utf-8"),
    )
    assert before == after

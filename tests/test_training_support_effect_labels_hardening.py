from __future__ import annotations

import json
from pathlib import Path

from scripts.harden_training_support_effect_labels import harden
from scripts.translation_review_common import community_term_matches, load_community_terms


def _write(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _seed(tmp_path: Path) -> Path:
    _write(tmp_path / "glossary/ui_community_terms.json", {"terms": []})
    harden(tmp_path)
    return tmp_path


def _record(root: Path, source: str, target: str, record_id: str, path: list[str] | None = None):
    terms = load_community_terms(root)
    matches = community_term_matches(
        None,
        source,
        target,
        terms,
        source_path="text_data_dict.json",
        json_path=path or ["155", "30003"],
    )
    return next(item for item in matches if item["id"] == record_id)


def test_friendship_bonus_scoped_positive_and_calque(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    good = _record(root, "友情加成&初始速度提升", "Friendship Bonus & Initial Speed", "support.friendship_bonus.effect155")
    assert good["accepted_present"] is True
    bad = _record(root, "友情加成&初始速度提升", "Thưởng tình bạn & Tăng Speed ban đầu", "support.friendship_bonus.effect155")
    assert bad["accepted_present"] is False and bad["forbidden_present"] is True


def test_training_effectiveness_scoped_positive_and_negative_prose(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    good = _record(root, "训练效果提升&初始牵绊值提升", "Training Effectiveness & Initial Friendship", "support.training_effectiveness.effect155")
    assert good["accepted_present"] is True
    terms = load_community_terms(root)
    assert community_term_matches(None, "训练效果提升", "tăng hiệu quả huấn luyện", terms, source_path="story.json", json_path=["1"]) == []


def test_mood_effect_and_initial_friendship(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    mood = _record(root, "干劲效果提升&初始牵绊值提升", "Mood Effect & Initial Friendship", "support.mood_effect.effect155")
    initial = _record(root, "干劲效果提升&初始牵绊值提升", "Mood Effect & Initial Friendship", "support.initial_friendship.effect155")
    assert mood["accepted_present"] is True
    assert initial["accepted_present"] is True


def test_specialty_priority_scoped(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    good = _record(root, "友情加成&得意率提升", "Friendship Bonus & Specialty Priority", "support.specialty_priority.effect155")
    assert good["accepted_present"] is True
    terms = load_community_terms(root)
    assert community_term_matches(None, "得意率提升", "Tăng tỷ lệ sở trường", terms, source_path="story.json", json_path=["1"]) == []


def test_effect_label_hardener_is_idempotent(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    path = root / "glossary/ui_community_terms.json"
    before = path.read_text(encoding="utf-8")
    harden(root)
    after = path.read_text(encoding="utf-8")
    assert before == after

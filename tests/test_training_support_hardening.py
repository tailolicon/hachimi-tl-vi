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
    _write(glossary / "term_registry.json", {"terms": [{
        "id": "system.friendship_training",
        "category": "training",
        "ja": ["友情トレーニング"],
        "zh_cn": ["友情训练"],
        "target_vi": "Huấn luyện Hữu nghị",
        "locked": True,
    }]})
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
    assert "system.friendship_training" in _ids(locked_term_matches(source, target, locked, source_path="text_data_dict.json", json_path=["143", "100"]))
    assert "common.friendship_training" in _ids(community_term_matches(None, source, target, community, source_path="text_data_dict.json", json_path=["143", "100"]))


def test_friendship_training_rejects_historical_calques(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    community = load_community_terms(root)
    matches = community_term_matches(None, "友情训练", "Huấn luyện tình bạn", community, source_path="text_data_dict.json", json_path=["143", "100"])
    record = next(item for item in matches if item["id"] == "common.friendship_training")
    assert record["accepted_present"] is False
    assert record["forbidden_present"] is True


def test_bare_friendship_or_training_prose_does_not_match(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    locked = load_locked_terms(root)
    community = load_community_terms(root)
    for source in ("友情加深了", "今天继续训练", "支持朋友的训练"):
        assert "system.friendship_training" not in _ids(locked_term_matches(source, "Câu văn tự nhiên", locked, source_path="story.json", json_path=["1"]))
        assert "common.friendship_training" not in _ids(community_term_matches(None, source, "Câu văn tự nhiên", community, source_path="story.json", json_path=["1"]))


def test_hardener_is_idempotent(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    before = (root / "glossary/term_registry.json").read_text(encoding="utf-8"), (root / "glossary/ui_community_terms.json").read_text(encoding="utf-8")
    harden(root)
    after = (root / "glossary/term_registry.json").read_text(encoding="utf-8"), (root / "glossary/ui_community_terms.json").read_text(encoding="utf-8")
    assert before == after

from __future__ import annotations

import json
from pathlib import Path

from scripts.harden_training_support_labels import harden
from scripts.translation_review_common import community_term_matches, load_community_terms, load_locked_terms, locked_term_matches


def _write(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _seed(tmp_path: Path) -> Path:
    glossary = tmp_path / "glossary"
    _write(glossary / "term_registry.json", {"terms": []})
    _write(glossary / "ui_community_terms.json", {"terms": []})
    harden(tmp_path)
    return tmp_path


def _ids(items: list[dict[str, object]]) -> set[str]:
    return {str(item.get("id")) for item in items}


def test_training_level_is_scoped_to_outgame352008(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    locked = load_locked_terms(root)
    community = load_community_terms(root)

    source = "训练等级"
    target = "Training Level"
    assert "training.level.outgame352008" in _ids(
        locked_term_matches(source, target, locked, source_path="localize_dict.json", json_path=["Outgame352008"])
    )
    matches = community_term_matches(
        "Outgame352008",
        source,
        target,
        community,
        source_path="localize_dict.json",
        json_path=["Outgame352008"],
    )
    record = next(item for item in matches if item["id"] == "common.training_level.outgame352008")
    assert record["accepted_present"] is True
    assert record["forbidden_present"] is False

    assert "training.level.outgame352008" not in _ids(
        locked_term_matches(source, "Cấp huấn luyện", locked, source_path="story.json", json_path=["1"])
    )
    assert community_term_matches(None, source, "Cấp huấn luyện", community, source_path="story.json", json_path=["1"]) == []


def test_training_level_rejects_historical_calque(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    community = load_community_terms(root)
    matches = community_term_matches(
        "Outgame352008",
        "训练等级",
        "Cấp huấn luyện",
        community,
        source_path="localize_dict.json",
        json_path=["Outgame352008"],
    )
    record = next(item for item in matches if item["id"] == "common.training_level.outgame352008")
    assert record["accepted_present"] is False
    assert record["forbidden_present"] is True


def test_failure_rate_is_scoped_to_singlemode0036(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    locked = load_locked_terms(root)
    community = load_community_terms(root)

    source = "失败率"
    target = "Failure Rate"
    assert "training.failure_rate.singlemode0036" in _ids(
        locked_term_matches(source, target, locked, source_path="localize_dict.json", json_path=["SingleMode0036"])
    )
    matches = community_term_matches(
        "SingleMode0036",
        source,
        target,
        community,
        source_path="localize_dict.json",
        json_path=["SingleMode0036"],
    )
    record = next(item for item in matches if item["id"] == "common.failure_rate.singlemode0036")
    assert record["accepted_present"] is True
    assert record["forbidden_present"] is False

    assert "training.failure_rate.singlemode0036" not in _ids(
        locked_term_matches(source, "Tỷ lệ thất bại", locked, source_path="story.json", json_path=["1"])
    )
    assert community_term_matches(None, source, "Tỷ lệ thất bại", community, source_path="story.json", json_path=["1"]) == []


def test_failure_rate_rejects_historical_calque(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    community = load_community_terms(root)
    matches = community_term_matches(
        "SingleMode0036",
        "失败率",
        "Tỷ lệ thất bại",
        community,
        source_path="localize_dict.json",
        json_path=["SingleMode0036"],
    )
    record = next(item for item in matches if item["id"] == "common.failure_rate.singlemode0036")
    assert record["accepted_present"] is False
    assert record["forbidden_present"] is True


def test_labels_hardener_is_idempotent(tmp_path: Path) -> None:
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

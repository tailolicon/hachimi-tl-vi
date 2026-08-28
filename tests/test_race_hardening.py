from __future__ import annotations

import json
from pathlib import Path

from scripts.harden_race_canon import harden
from scripts.translation_review_common import (
    canonical_finding_matches,
    community_term_matches,
    item_scoped_context_hash,
    load_community_terms,
    load_locked_terms,
    locked_term_matches,
)


def _write(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _seed(tmp_path: Path) -> Path:
    glossary = tmp_path / "glossary"
    _write(glossary / "term_registry.json", {"terms": [
        {"id": "race.generic", "category": "race", "ja": ["レース"], "zh_cn": ["比赛"], "target_vi": "Cuộc đua", "locked": True},
        {"id": "race.surface.turf", "category": "race_surface", "ja": ["芝"], "zh_cn": ["草地"], "target_vi": "Turf", "locked": True},
        {"id": "race.surface.dirt", "category": "race_surface", "ja": ["ダート"], "zh_cn": ["泥地"], "target_vi": "Dirt", "locked": True},
        {"id": "race.distance.sprint", "category": "distance", "ja": ["短距離"], "zh_cn": ["短距离"], "target_vi": "Sprint", "locked": True},
        {"id": "race.distance.mile", "category": "distance", "ja": ["マイル"], "zh_cn": ["英里"], "target_vi": "Mile", "locked": True},
        {"id": "race.distance.medium", "category": "distance", "ja": ["中距離"], "zh_cn": ["中距离"], "target_vi": "Medium", "locked": True},
        {"id": "race.distance.long", "category": "distance", "ja": ["長距離"], "zh_cn": ["长距离"], "target_vi": "Long", "locked": True},
        {"id": "race.strategy.style", "category": "running_style", "ja": ["作戦"], "zh_cn": ["跑法"], "target_vi": "Style", "locked": True},
        {"id": "race.strategy.front_runner", "category": "running_style", "ja": ["逃げ"], "zh_cn": ["领跑"], "target_vi": "Front Runner", "locked": True},
        {"id": "race.strategy.pace_chaser", "category": "running_style", "ja": ["先行"], "zh_cn": ["先行"], "target_vi": "Pace Chaser", "locked": True},
        {"id": "race.strategy.late_surger", "category": "running_style", "ja": ["差し"], "zh_cn": ["差行"], "target_vi": "Late Surger", "locked": True},
        {"id": "race.strategy.end_closer", "category": "running_style", "ja": ["追込"], "zh_cn": ["追赶"], "target_vi": "End Closer", "locked": True},
        {"id": "race.strategy.runaway", "category": "running_style", "ja": ["大逃げ"], "zh_cn": ["爆领"], "target_vi": "Runaway", "locked": True},
        {"id": "race.miyako_stakes", "category": "race", "ja": ["みやこステークス"], "zh_cn": ["京城锦标"], "target_vi": "Miyako Stakes", "locked": True},
        {"id": "reviewed.race_name.867d16270a74", "category": "race_name", "ja": ["日本ダービー"], "zh_cn": ["日本德比"], "target_vi": "Japanese Derby", "locked": True},
    ]})
    _write(glossary / "ui_community_terms.json", {"terms": []})
    _write(glossary / "source_bridge_terms.json", {"schema_version": 1, "policy": {}, "terms": [], "untrusted_sources": []})
    harden(tmp_path)
    return tmp_path


def _ids(matches: list[dict[str, object]]) -> set[str]:
    return {str(item.get("id")) for item in matches}


def test_preserves_core_surface_distance_and_running_style_terms(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    terms = load_locked_terms(root)
    cases = [
        ("草地", "Turf", "race.surface.turf"), ("泥地", "Dirt", "race.surface.dirt"),
        ("短距离", "Sprint", "race.distance.sprint"), ("英里", "Mile", "race.distance.mile"),
        ("中距离", "Medium", "race.distance.medium"), ("长距离", "Long", "race.distance.long"),
        ("跑法", "Style", "race.strategy.style"), ("领跑", "Front Runner", "race.strategy.front_runner"),
        ("先行", "Pace Chaser", "race.strategy.pace_chaser"), ("差行", "Late Surger", "race.strategy.late_surger"),
        ("追赶", "End Closer", "race.strategy.end_closer"), ("爆领", "Runaway", "race.strategy.runaway"),
    ]
    for source, target, expected in cases:
        assert expected in _ids(locked_term_matches(source, target, terms, source_path="localize_dict.json", json_path=["RaceX"]))


def test_race_classes_are_context_scoped_and_story_prose_is_negative(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    terms = load_locked_terms(root)
    assert "race.class.junior.ui" in _ids(locked_term_matches("新马级", "Junior Class", terms, key="SingleMode0017", source_path="localize_dict.json", json_path=["SingleMode0017"]))
    assert "race.class.classic.ui" in _ids(locked_term_matches("经典级", "Classic Class", terms, key="SingleMode0018", source_path="localize_dict.json", json_path=["SingleMode0018"]))
    assert "race.class.senior.ui" in _ids(locked_term_matches("古马级", "Senior Class", terms, key="SingleMode0019", source_path="localize_dict.json", json_path=["SingleMode0019"]))
    assert not any(item.startswith("race.class.") for item in _ids(locked_term_matches(
        "在新马级比赛中表现出色的希望之星", "Những ngôi sao nổi bật trong các cuộc đua tân mã", terms,
        source_path="text_data_dict.json", json_path=["128", "1007"])))


def test_grades_use_g1_g2_g3_and_short_open_labels_are_exact(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    locked = load_locked_terms(root)
    community = load_community_terms(root)
    for source, target, rid in (("GⅠ", "G1", "race.grade.g1"), ("GⅡ", "G2", "race.grade.g2"), ("GⅢ", "G3", "race.grade.g3")):
        assert rid in _ids(locked_term_matches(source, target, locked, source_path="localize_dict.json", json_path=["Menu"]));
        assert f"common.{rid}" in _ids(community_term_matches(None, source, target, community, source_path="localize_dict.json", json_path=["Menu"]))
    assert "race.grade.open" in _ids(locked_term_matches("OP", "OP", locked, key="Race0025", source_path="localize_dict.json", json_path=["Race0025"]))
    assert "race.grade.pre_open" in _ids(locked_term_matches("Pre-OP比赛", "Cuộc đua Pre-OP", locked, key="SingleMode0493", source_path="localize_dict.json", json_path=["SingleMode0493"]))
    assert "race.grade.open" not in _ids(locked_term_matches("OPENING", "OPENING", locked, source_path="text_data_dict.json", json_path=["163", "1"]))


def test_racecourses_are_item_scoped_and_do_not_match_generic_place_prose(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    terms = load_locked_terms(root)
    assert "racecourse.tokyo" in _ids(locked_term_matches("东京", "Tokyo", terms, source_path="text_data_dict.json", json_path=["35", "10006"]))
    assert "racecourse.hakodate" in _ids(locked_term_matches("在札幌或函馆竞马场获胜", "Thắng tại Sapporo hoặc Hakodate", terms, source_path="text_data_dict.json", json_path=["131", "218"]))
    assert "racecourse.tokyo" not in _ids(locked_term_matches("我去了东京旅行", "Tôi đi du lịch Tokyo", terms, source_path="text_data_dict.json", json_path=["163", "1"]))
    record = next(term for term in terms if term["id"] == "racecourse.tokyo")
    assert record["invalidation_scope"] == "item"


def test_named_races_use_single_verified_targets(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    terms = load_locked_terms(root)
    checks = (
        ("日本德比", "Japanese Derby (Tokyo Yushun)", "race.tokyo_yushun"),
        ("优骏牝马（日本橡树大赛）", "Japanese Oaks", "race.japanese_oaks"),
        ("樱花赏", "Oka Sho", "race.oka_sho"),
        ("冠军杯", "Champions Cup", "race.champions_cup"),
        ("朝日杯未来锦标", "Asahi Hai Futurity Stakes", "race.asahi_hai_futurity_stakes"),
        ("关东橡树大赛", "Kanto Oaks", "race.kanto_oaks"),
        ("凯旋门赏", "Prix de l'Arc de Triomphe", "race.prix_arc_de_triomphe"),
    )
    for source, target, rid in checks:
        assert rid in _ids(locked_term_matches(source, target, terms, source_path="text_data_dict.json", json_path=["111", "1"]))
    obsolete = next(term for term in terms if term["id"] == "reviewed.race_name.867d16270a74")
    assert obsolete["locked"] is False and obsolete["zh_cn"] == []


def test_miyako_zh_collision_is_scoped_away_from_retrospective_category_111(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    terms = load_locked_terms(root)
    assert "race.miyako_stakes" in _ids(locked_term_matches("京城锦标", "Miyako Stakes", terms, source_path="text_data_dict.json", json_path=["32", "3061"]))
    assert "race.miyako_stakes" not in _ids(locked_term_matches("京城锦标", "Keio Hai Junior Stakes", terms, source_path="text_data_dict.json", json_path=["111", "134"]))


def test_track_condition_direction_and_course_shape_are_exact_race_ui(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    terms = load_locked_terms(root)
    for key, source, target, rid in (
        ("Race0186", "良", "Firm", "race.track_condition.firm"),
        ("Race0187", "稍重", "Good", "race.track_condition.good"),
        ("Race0188", "重", "Soft", "race.track_condition.soft"),
        ("Race0189", "不良", "Heavy", "race.track_condition.heavy"),
        ("Race0190", "内圈", "Inner", "race.course.inner"),
        ("Race0191", "外圈", "Outer", "race.course.outer"),
        ("Race0192", "逆时针", "Left", "race.course.left"),
        ("Race0193", "顺时针", "Right", "race.course.right"),
    ):
        assert rid in _ids(locked_term_matches(source, target, terms, key=key, source_path="localize_dict.json", json_path=[key]))
    assert "race.track_condition.soft" not in _ids(locked_term_matches("重大的比赛", "Cuộc đua quan trọng", terms, source_path="text_data_dict.json", json_path=["163", "9"]))


def test_semantic_zh_race_bridges_are_narrow_and_generic_words_do_not_match(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    bridge = json.loads((root / "glossary/source_bridge_terms.json").read_text(encoding="utf-8"))["terms"]
    from scripts.translation_review_common import source_bridge_term_matches
    matched = source_bridge_term_matches("长途锦标", "Stayers Stakes", bridge, source_path="text_data_dict.json", json_path=["111", "1"])
    assert any(item["id"] == "race.bridge.stayers_stakes" for item in matched)
    for source in ("这是一场比赛", "赢得一个杯子", "经典的德比故事", "最后的冠军"):
        assert not any(str(item.get("id", "")).startswith("race.bridge.") for item in source_bridge_term_matches(source, source, bridge, source_path="text_data_dict.json", json_path=["163", "1"]))


def test_proper_name_substrings_do_not_create_generic_named_race_matches(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    terms = load_locked_terms(root)
    ids = _ids(locked_term_matches("这是普通的冠军杯子，不是赛事名", "Đây chỉ là chiếc cúp của nhà vô địch", terms, source_path="text_data_dict.json", json_path=["163", "1"]))
    assert "race.champions_cup" not in ids
    assert "race.tokyo_yushun" not in _ids(locked_term_matches("德比是一种赛事称呼", "Derby là một cách gọi cuộc đua", terms, source_path="text_data_dict.json", json_path=["163", "2"]))


def test_named_race_item_context_changes_only_matching_entry(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    locked = load_locked_terms(root)
    community = load_community_terms(root)
    derby_before = item_scoped_context_hash(key=None, source="日本德比", source_path="text_data_dict.json", json_path=["111", "12"], locked_terms=locked, community_terms=community)
    unrelated_before = item_scoped_context_hash(key=None, source="普通的故事文本", source_path="text_data_dict.json", json_path=["163", "1"], locked_terms=locked, community_terms=community)
    registry_path = root / "glossary/term_registry.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    next(term for term in registry["terms"] if term["id"] == "race.tokyo_yushun")["target_vi"] = "Japanese Derby (Tokyo Yushun) v2"
    _write(registry_path, registry)
    locked_after = load_locked_terms(root)
    derby_after = item_scoped_context_hash(key=None, source="日本德比", source_path="text_data_dict.json", json_path=["111", "12"], locked_terms=locked_after, community_terms=community)
    unrelated_after = item_scoped_context_hash(key=None, source="普通的故事文本", source_path="text_data_dict.json", json_path=["163", "1"], locked_terms=locked_after, community_terms=community)
    assert derby_before and derby_after and derby_before != derby_after
    assert unrelated_before == unrelated_after is None


def test_removed_race_rule_invalidates_prior_item_context(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    locked = load_locked_terms(root)
    community = load_community_terms(root)
    before = item_scoped_context_hash(key=None, source="樱花赏", source_path="text_data_dict.json", json_path=["111", "1"], locked_terms=locked, community_terms=community)
    registry_path = root / "glossary/term_registry.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    registry["terms"] = [term for term in registry["terms"] if term.get("id") != "race.oka_sho"]
    _write(registry_path, registry)
    after = item_scoped_context_hash(key=None, source="樱花赏", source_path="text_data_dict.json", json_path=["111", "1"], locked_terms=load_locked_terms(root), community_terms=community)
    assert before is not None and after != before


def test_open_canonical_finding_is_item_scoped_and_changes_context(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    finding = {
        "finding_id": "cf-race-test", "status": "open", "source_zh_cn": "未知杯",
        "match_mode": "exact", "source_paths": ["text_data_dict.json"], "key_exact": [],
        "json_path_prefixes": [["111"]], "suggested_targets_vi": ["Unknown Cup"],
        "concepts": ["race_name"], "kinds": ["proper_name"],
    }
    matched = canonical_finding_matches(None, "未知杯", [finding], source_path="text_data_dict.json", json_path=["111", "77"])
    assert matched and matched[0]["finding_id"] == "cf-race-test"
    assert canonical_finding_matches(None, "未知杯", [finding], source_path="text_data_dict.json", json_path=["163", "77"]) == []
    assert item_scoped_context_hash(key=None, source="未知杯", source_path="text_data_dict.json", json_path=["111", "77"], locked_terms=load_locked_terms(root), community_terms=load_community_terms(root), canonical_findings=matched) is not None


def test_race_hardener_is_idempotent(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    paths = [root / "glossary/term_registry.json", root / "glossary/ui_community_terms.json", root / "glossary/source_bridge_terms.json"]
    before = [path.read_text(encoding="utf-8") for path in paths]
    harden(root)
    assert [path.read_text(encoding="utf-8") for path in paths] == before

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
    if old not in text:
        raise RuntimeError(f"expected text not found in {path}: {old[:100]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def clean_builder_imports() -> None:
    path = ROOT / "scripts/build_translation_review_plan.py"
    text = path.read_text(encoding="utf-8")
    marker = "TRANSLATION_REVIEW_POLICY_VERSION = 3"
    if marker not in text:
        raise RuntimeError("builder policy marker missing")
    _, tail = text.split(marker, 1)
    header = '''from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any

try:
    from scripts.translation_review_common import (
        canonical_finding_matches,
        community_term_matches,
        context_snapshot_hash,
        get_json_path,
        item_scoped_context_hash,
        item_scoped_policy_hash,
        load_canonical_findings,
        load_community_terms,
        load_json,
        load_locked_terms,
        load_skill_examples,
        load_source_bridge_config,
        locked_term_matches,
        risk_metadata,
        source_bridge_policy_hash,
        source_bridge_risk_matches,
        source_bridge_term_matches,
        suppress_overridden_locked_terms,
        text_fingerprint,
        utc_now,
        write_json,
    )
except ModuleNotFoundError:
    from translation_review_common import (  # type: ignore[no-redef]
        canonical_finding_matches,
        community_term_matches,
        context_snapshot_hash,
        get_json_path,
        item_scoped_context_hash,
        item_scoped_policy_hash,
        load_canonical_findings,
        load_community_terms,
        load_json,
        load_locked_terms,
        load_skill_examples,
        load_source_bridge_config,
        locked_term_matches,
        risk_metadata,
        source_bridge_policy_hash,
        source_bridge_risk_matches,
        source_bridge_term_matches,
        suppress_overridden_locked_terms,
        text_fingerprint,
        utc_now,
        write_json,
    )

'''
    path.write_text(header + marker + tail, encoding="utf-8")


def patch_hardener() -> None:
    path = ROOT / "scripts/harden_race_canon.py"
    text = path.read_text(encoding="utf-8")
    text = text.replace('"target_vi": "Japanese Derby (Tokyo Yushun)"', '"target_vi": "Japanese Derby"')
    text = text.replace(
        '"note": "Player-facing Global form is Japanese Derby (Tokyo Yushun); JRA identity is 東京優駿 / Tokyo Yushun (Japanese Derby). One canonical target prevents Japan Derby/Japanese Derby/Tokyo Yushun split-brain."',
        '"note": "Canonical player-facing form is Japanese Derby; JP identity is 東京優駿 / Tokyo Yushun. One target prevents legacy Japan Derby/Japanese Derby/Tokyo Yushun split-brain."',
    )
    text = text.replace('"target_vi": "Radio Nikkei Sho"', '"target_vi": "Radio NIKKEI Sho"')

    entries = '''    "race.tokyo_sports_hai_nisai_stakes": {"zh_cn": ["东京体育杯新马锦标"], "ja": ["東京スポーツ杯2歳ステークス"], "target_vi": "Tokyo Sports Hai Nisai Stakes", "note": "Verified JRA/in-game identity; preserve Nisai instead of semantic-calquing the zh-CN title."},
    "race.keio_hai_nisai_stakes": {"zh_cn": ["京王杯新马锦标"], "ja": ["京王杯2歳ステークス"], "target_vi": "Keio Hai Nisai Stakes", "note": "Verified JRA/in-game identity; lossy zh-CN 京城锦标 is handled separately by an exact retrospective slot rule."},
    "race.hakodate_nisai_stakes": {"zh_cn": ["函馆新马锦标"], "ja": ["函館2歳ステークス"], "target_vi": "Hakodate Nisai Stakes", "note": "Verified JRA/in-game identity."},
    "race.sapporo_nisai_stakes": {"zh_cn": ["札幌新马锦标"], "ja": ["札幌2歳ステークス"], "target_vi": "Sapporo Nisai Stakes", "note": "Verified JRA/in-game identity."},
    "race.nakayama_himba_stakes": {"zh_cn": ["中山赛马娘锦标"], "ja": ["中山牝馬ステークス"], "target_vi": "Nakayama Himba Stakes", "note": "Verified JRA/in-game identity; zh-CN semantic wording is not spelling authority."},
    "race.kyoto_himba_stakes": {"zh_cn": ["京都赛马娘锦标"], "ja": ["京都牝馬ステークス"], "target_vi": "Kyoto Himba Stakes", "note": "Verified historical JRA/in-game identity."},
    "race.hanshin_himba_stakes": {"zh_cn": ["阪神赛马娘锦标"], "ja": ["阪神牝馬ステークス"], "target_vi": "Hanshin Himba Stakes", "note": "Verified JRA/in-game identity."},
'''
    marker = '\n}\n\nBRIDGE_RACES = {'
    if "race.tokyo_sports_hai_nisai_stakes" not in text:
        if marker not in text:
            raise RuntimeError("RACES/BRIDGE_RACES boundary missing")
        text = text.replace(marker, '\n' + entries + '}\n\nBRIDGE_RACES = {', 1)

    old_existing_scope = '''        if isinstance(term, dict) and bool(term.get("locked")) and _is_proper_race(term):
            term["invalidation_scope"] = "item"
'''
    new_existing_scope = '''        if isinstance(term, dict) and bool(term.get("locked")) and _is_proper_race(term):
            term["source_paths"] = ["text_data_dict.json"]
            term["json_path_prefixes"] = [["32"], ["33"], ["111"]]
            term["match_mode"] = "contains"
            term["invalidation_scope"] = "item"
'''
    if old_existing_scope in text:
        text = text.replace(old_existing_scope, new_existing_scope, 1)
    elif new_existing_scope not in text:
        raise RuntimeError("existing proper-race scope block missing")

    old_record_scope = '''            "target_vi": spec["target_vi"],
            "locked": True,
            "match_mode": "contains",
            "invalidation_scope": "item",
'''
    new_record_scope = '''            "target_vi": spec["target_vi"],
            "locked": True,
            "source_paths": ["text_data_dict.json"],
            "json_path_prefixes": [["32"], ["33"], ["111"]],
            "match_mode": "contains",
            "invalidation_scope": "item",
'''
    if old_record_scope in text:
        text = text.replace(old_record_scope, new_record_scope, 1)
    elif new_record_scope not in text:
        raise RuntimeError("new proper-race record scope block missing")

    collision_rule = '''    _upsert(terms, {
        "id": "race.keio_hai_nisai_stakes.zhcollapse_111_134",
        "category": "race_name",
        "ja": ["京王杯2歳ステークス"],
        "zh_cn": ["京城锦标"],
        "target_vi": "Keio Hai Nisai Stakes",
        "locked": True,
        "source_paths": ["text_data_dict.json"],
        "json_path_prefixes": [["111", "134"]],
        "match_mode": "exact",
        "invalidation_scope": "item",
        "note": "At retrospective identity 111/134, lossy zh-CN 京城锦标 is Keio Hai Nisai Stakes. Keep it structurally distinct from Miyako Stakes at 32/3061 and 33/3061.",
    })

'''
    class_marker = '    # Race classes: exact primary UI labels plus explicitly race-oriented text\n'
    if "race.keio_hai_nisai_stakes.zhcollapse_111_134" not in text:
        if class_marker not in text:
            raise RuntimeError("Race-class insertion marker missing")
        text = text.replace(class_marker, collision_rule + class_marker, 1)

    path.write_text(text, encoding="utf-8")


def patch_race_tests() -> None:
    path = ROOT / "tests/test_race_hardening.py"
    text = path.read_text(encoding="utf-8")
    text = text.replace('("日本德比", "Japanese Derby (Tokyo Yushun)", "race.tokyo_yushun")', '("日本德比", "Japanese Derby", "race.tokyo_yushun")')

    start = text.find("def test_miyako_zh_collision_is_scoped_away_from_retrospective_category_111")
    end = text.find("def test_track_condition_direction_and_course_shape_are_exact_race_ui", start)
    if start >= 0 and end > start:
        replacement = '''def test_same_zh_collapse_resolves_to_two_contextual_race_identities(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    terms = load_locked_terms(root)
    miyako = locked_term_matches("京城锦标", "Miyako Stakes", terms, source_path="text_data_dict.json", json_path=["32", "3061"])
    keio = locked_term_matches("京城锦标", "Keio Hai Nisai Stakes", terms, source_path="text_data_dict.json", json_path=["111", "134"])
    assert "race.miyako_stakes" in _ids(miyako)
    assert "race.keio_hai_nisai_stakes.zhcollapse_111_134" in _ids(keio)
    assert "race.miyako_stakes" not in _ids(keio)
    assert "race.keio_hai_nisai_stakes.zhcollapse_111_134" not in _ids(miyako)

    community = load_community_terms(root)
    miyako_hash = item_scoped_context_hash(key=None, source="京城锦标", source_path="text_data_dict.json", json_path=["32", "3061"], locked_terms=terms, community_terms=community)
    keio_hash = item_scoped_context_hash(key=None, source="京城锦标", source_path="text_data_dict.json", json_path=["111", "134"], locked_terms=terms, community_terms=community)
    assert miyako_hash is not None and keio_hash is not None and miyako_hash != keio_hash


def test_named_race_identity_variants_are_canonical_and_scoped(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    terms = load_locked_terms(root)
    checks = (
        ("天皇赏（春）", "Tenno Sho (Spring)", "race.tenno_sho_spring"),
        ("天皇赏（秋）", "Tenno Sho (Autumn)", "race.tenno_sho_autumn"),
        ("菊花赏", "Kikuka Sho", "race.kikuka_sho"),
        ("日经广播赏", "Radio NIKKEI Sho", "race.radio_nikkei_sho"),
    )
    for source, target, rid in checks:
        assert rid in _ids(locked_term_matches(source, target, terms, source_path="text_data_dict.json", json_path=["111", "9"]))
    assert "race.tenno_sho_spring" not in _ids(locked_term_matches("天皇赏（秋）", "Tenno Sho (Autumn)", terms, source_path="text_data_dict.json", json_path=["111", "9"]))


def test_song_category_and_objective_prose_do_not_receive_proper_race_context(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    terms = load_locked_terms(root)
    song_ids = _ids(locked_term_matches("日本德比", "Japanese Derby", terms, source_path="text_data_dict.json", json_path=["16", "9001"]))
    assert "race.tokyo_yushun" not in song_ids
    objective_ids = _ids(locked_term_matches("经典比赛的目标是在最终比赛获胜", "Mục tiêu là thắng cuộc đua cuối", terms, source_path="text_data_dict.json", json_path=["147", "44"]))
    assert not any(rid.startswith("race.") and rid != "race.generic" for rid in objective_ids)


def test_removing_named_race_rule_invalidates_only_matching_item_context(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    locked = load_locked_terms(root)
    community = load_community_terms(root)
    affected_before = item_scoped_context_hash(key=None, source="日本德比", source_path="text_data_dict.json", json_path=["111", "12"], locked_terms=locked, community_terms=community)
    unrelated_before = item_scoped_context_hash(key=None, source="普通文本", source_path="text_data_dict.json", json_path=["163", "1"], locked_terms=locked, community_terms=community)
    registry_path = root / "glossary/term_registry.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    registry["terms"] = [term for term in registry["terms"] if term.get("id") != "race.tokyo_yushun"]
    _write(registry_path, registry)
    locked_after = load_locked_terms(root)
    affected_after = item_scoped_context_hash(key=None, source="日本德比", source_path="text_data_dict.json", json_path=["111", "12"], locked_terms=locked_after, community_terms=community)
    unrelated_after = item_scoped_context_hash(key=None, source="普通文本", source_path="text_data_dict.json", json_path=["163", "1"], locked_terms=locked_after, community_terms=community)
    assert affected_before is not None and affected_after != affected_before
    assert unrelated_before == unrelated_after


'''
        text = text[:start] + replacement + text[end:]
    elif "def test_same_zh_collapse_resolves_to_two_contextual_race_identities" not in text:
        raise RuntimeError("collision test block missing")

    path.write_text(text, encoding="utf-8")


def patch_production_sync() -> None:
    path = ROOT / ".github/workflows/sync-translation-review-plan.yml"
    text = path.read_text(encoding="utf-8")
    if '      - "scripts/harden_race_canon.py"\n' not in text:
        text = text.replace('      - "scripts/harden_skill_inheritance_canon.py"\n', '      - "scripts/harden_skill_inheritance_canon.py"\n      - "scripts/harden_race_canon.py"\n', 1)
    if '      - "tests/test_race_hardening.py"\n' not in text:
        text = text.replace('      - "tests/test_skill_inheritance_hardening.py"\n', '      - "tests/test_skill_inheritance_hardening.py"\n      - "tests/test_race_hardening.py"\n      - "tests/test_review_gate_idempotence.py"\n', 1)
    if "python scripts/harden_race_canon.py" not in text:
        text = text.replace('          python scripts/harden_skill_inheritance_canon.py\n', '          python scripts/harden_skill_inheritance_canon.py\n          python scripts/harden_race_canon.py\n', 1)
    add_anchor = '            scripts/harden_skill_inheritance_canon.py \\\n'
    if '            scripts/harden_race_canon.py \\\n' not in text:
        if add_anchor not in text:
            raise RuntimeError("sync git-add hardener anchor missing")
        text = text.replace(add_anchor, add_anchor + '            scripts/harden_race_canon.py \\\n', 1)
    test_anchor = '            tests/test_skill_inheritance_hardening.py \\\n'
    if '            tests/test_race_hardening.py \\\n' not in text:
        if test_anchor not in text:
            raise RuntimeError("sync git-add test anchor missing")
        text = text.replace(test_anchor, test_anchor + '            tests/test_race_hardening.py \\\n            tests/test_review_gate_idempotence.py \\\n', 1)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    clean_builder_imports()
    patch_hardener()
    patch_race_tests()
    patch_production_sync()
    from harden_race_canon import harden
    harden(ROOT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

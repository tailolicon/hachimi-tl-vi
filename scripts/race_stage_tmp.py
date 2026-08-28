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
    text = text.replace('"target": "Japanese Derby (Tokyo Yushun)"', '"target": "Japanese Derby"')
    text = text.replace('"target": "Radio Nikkei Sho"', '"target": "Radio NIKKEI Sho"')

    anchor = '''    {"id": "race.hankyu_hai", "ja": ["阪急杯"], "zh": ["阪急杯"], "target": "Hankyu Hai", "note": "Official JRA English race identity."},\n'''
    additions = '''    {"id": "race.hankyu_hai", "ja": ["阪急杯"], "zh": ["阪急杯"], "target": "Hankyu Hai", "note": "Official JRA English race identity."},
    {"id": "race.tokyo_sports_hai_nisai_stakes", "ja": ["東京スポーツ杯2歳ステークス"], "zh": ["东京体育杯新马锦标"], "target": "Tokyo Sports Hai Nisai Stakes", "note": "Verified JRA/in-game race identity; preserve Nisai rather than literal zh-CN wording."},
    {"id": "race.keio_hai_nisai_stakes", "ja": ["京王杯2歳ステークス"], "zh": ["京王杯新马锦标"], "target": "Keio Hai Nisai Stakes", "note": "Verified JRA/in-game race identity; separate from the lossy zh-CN collapse 京城锦标 handled by an exact category/item rule."},
    {"id": "race.hakodate_nisai_stakes", "ja": ["函館2歳ステークス"], "zh": ["函馆新马锦标"], "target": "Hakodate Nisai Stakes", "note": "Verified JRA/in-game race identity."},
    {"id": "race.sapporo_nisai_stakes", "ja": ["札幌2歳ステークス"], "zh": ["札幌新马锦标"], "target": "Sapporo Nisai Stakes", "note": "Verified JRA/in-game race identity."},
    {"id": "race.nakayama_himba_stakes", "ja": ["中山牝馬ステークス"], "zh": ["中山赛马娘锦标"], "target": "Nakayama Himba Stakes", "note": "Verified JRA/in-game race identity; zh-CN semantic localization is not authoritative for spelling."},
    {"id": "race.kyoto_himba_stakes", "ja": ["京都牝馬ステークス"], "zh": ["京都赛马娘锦标"], "target": "Kyoto Himba Stakes", "note": "Verified historical JRA/in-game race identity."},
    {"id": "race.hanshin_himba_stakes", "ja": ["阪神牝馬ステークス"], "zh": ["阪神赛马娘锦标"], "target": "Hanshin Himba Stakes", "note": "Verified JRA/in-game race identity."},
'''
    if "race.tokyo_sports_hai_nisai_stakes" not in text:
        if anchor not in text:
            raise RuntimeError("race insertion anchor missing")
        text = text.replace(anchor, additions, 1)

    old_scope = '''        _upsert(terms, {
            "id": spec["id"], "category": "race_name", "ja": spec["ja"], "zh_cn": spec["zh"],
            "target_vi": spec["target"], "locked": True, "match_mode": "contains",
            "invalidation_scope": "item", "note": spec["note"],
        })
'''
    new_scope = '''        _upsert(terms, {
            "id": spec["id"], "category": "race_name", "ja": spec["ja"], "zh_cn": spec["zh"],
            "target_vi": spec["target"], "locked": True,
            "source_paths": ["text_data_dict.json"],
            "json_path_prefixes": [["32"], ["33"], ["111"]],
            "match_mode": "contains", "invalidation_scope": "item", "note": spec["note"],
        })
'''
    if old_scope in text:
        text = text.replace(old_scope, new_scope, 1)
    elif new_scope not in text:
        raise RuntimeError("proper-race scope block missing")

    same_target_old = '''            else:
                term["invalidation_scope"] = "item"
'''
    same_target_new = '''            else:
                term["source_paths"] = ["text_data_dict.json"]
                term["json_path_prefixes"] = [["32"], ["33"], ["111"]]
                term["match_mode"] = "contains"
                term["invalidation_scope"] = "item"
'''
    if same_target_old in text:
        text = text.replace(same_target_old, same_target_new, 1)
    elif same_target_new not in text:
        raise RuntimeError("existing proper-race scope block missing")

    miyako_anchor = '''            term["note"] = "Miyako Stakes only in pinned race identity slots 32/3061 and 33/3061; zh-CN 京城锦标 is lossy and collides with another race identity in retrospective category 111."


def _harden_registry'''
    collision = '''            term["note"] = "Miyako Stakes only in pinned race identity slots 32/3061 and 33/3061; zh-CN 京城锦标 is lossy and collides with another race identity in retrospective category 111."

    _upsert(terms, {
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
        "note": "The same lossy zh-CN string 京城锦标 is Keio Hai Nisai Stakes at retrospective identity 111/134; it must remain distinct from Miyako Stakes 32/3061 and 33/3061.",
    })


def _harden_registry'''
    if "race.keio_hai_nisai_stakes.zhcollapse_111_134" not in text:
        if miyako_anchor not in text:
            raise RuntimeError("Miyako collision anchor missing")
        text = text.replace(miyako_anchor, collision, 1)

    path.write_text(text, encoding="utf-8")


def patch_race_tests() -> None:
    path = ROOT / "tests/test_race_hardening.py"
    text = path.read_text(encoding="utf-8")
    text = text.replace('("日本德比", "Japanese Derby (Tokyo Yushun)", "race.tokyo_yushun")', '("日本德比", "Japanese Derby", "race.tokyo_yushun")')
    text = text.replace('assert "race.miyako_stakes" not in _ids(locked_term_matches("京城锦标", "Keio Hai Junior Stakes", terms, source_path="text_data_dict.json", json_path=["111", "134"]))', 'keio = locked_term_matches("京城锦标", "Keio Hai Nisai Stakes", terms, source_path="text_data_dict.json", json_path=["111", "134"])\n    assert "race.keio_hai_nisai_stakes.zhcollapse_111_134" in _ids(keio)\n    assert "race.miyako_stakes" not in _ids(keio)')

    marker = '''def test_track_condition_direction_and_course_shape_are_exact_race_ui(tmp_path: Path) -> None:\n'''
    extra = '''def test_named_race_identity_variants_are_canonical_and_scoped(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    terms = load_locked_terms(root)
    checks = (
        ("春季天皇赏", "Tenno Sho (Spring)", "race.tenno_sho_spring"),
        ("秋季天皇赏", "Tenno Sho (Autumn)", "race.tenno_sho_autumn"),
        ("菊花赏", "Kikuka Sho", "race.kikuka_sho"),
        ("日经广播赏", "Radio NIKKEI Sho", "race.radio_nikkei_sho"),
    )
    for source, target, rid in checks:
        assert rid in _ids(locked_term_matches(source, target, terms, source_path="text_data_dict.json", json_path=["111", "9"]))
    assert "race.tenno_sho_spring" not in _ids(locked_term_matches("秋季天皇赏", "Tenno Sho (Autumn)", terms, source_path="text_data_dict.json", json_path=["111", "9"]))
    assert "race.kikuka_sho" not in _ids(locked_term_matches("菊花赏", "Kikka Sho", terms, source_path="text_data_dict.json", json_path=["16", "1"]))


def test_same_zh_collapse_has_two_distinct_item_contexts(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    locked = load_locked_terms(root)
    community = load_community_terms(root)
    miyako_hash = item_scoped_context_hash(key=None, source="京城锦标", source_path="text_data_dict.json", json_path=["32", "3061"], locked_terms=locked, community_terms=community)
    keio_hash = item_scoped_context_hash(key=None, source="京城锦标", source_path="text_data_dict.json", json_path=["111", "134"], locked_terms=locked, community_terms=community)
    assert miyako_hash is not None and keio_hash is not None
    assert miyako_hash != keio_hash


def test_song_category_and_objective_prose_do_not_receive_proper_race_context(tmp_path: Path) -> None:
    root = _seed(tmp_path)
    terms = load_locked_terms(root)
    song_ids = _ids(locked_term_matches("日本德比", "Japanese Derby", terms, source_path="text_data_dict.json", json_path=["16", "9001"]))
    assert "race.tokyo_yushun" not in song_ids
    objective_ids = _ids(locked_term_matches("经典比赛的目标是在最终比赛获胜", "Mục tiêu là thắng cuộc đua cuối", terms, source_path="text_data_dict.json", json_path=["147", "44"]))
    assert not any(rid.startswith("race.") and rid not in {"race.generic"} for rid in objective_ids)


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
    if "test_named_race_identity_variants_are_canonical_and_scoped" not in text:
        if marker not in text:
            raise RuntimeError("race test insertion marker missing")
        text = text.replace(marker, extra + marker, 1)
    path.write_text(text, encoding="utf-8")


def patch_production_sync() -> None:
    path = ROOT / ".github/workflows/sync-translation-review-plan.yml"
    text = path.read_text(encoding="utf-8")
    if "scripts/harden_race_canon.py" not in text.split("workflow_dispatch:", 1)[0]:
        text = text.replace('      - "scripts/harden_skill_inheritance_canon.py"\n', '      - "scripts/harden_skill_inheritance_canon.py"\n      - "scripts/harden_race_canon.py"\n')
        text = text.replace('      - "tests/test_skill_inheritance_hardening.py"\n', '      - "tests/test_skill_inheritance_hardening.py"\n      - "tests/test_race_hardening.py"\n      - "tests/test_review_gate_idempotence.py"\n')
    if "python scripts/harden_race_canon.py" not in text:
        text = text.replace('          python scripts/harden_skill_inheritance_canon.py\n', '          python scripts/harden_skill_inheritance_canon.py\n          python scripts/harden_race_canon.py\n')
    if "scripts/harden_race_canon.py" not in text.split("if git diff --cached --quiet", 1)[0].split("git add", 1)[-1]:
        text = text.replace('            scripts/harden_skill_inheritance_canon.py \\\n', '            scripts/harden_skill_inheritance_canon.py \\\n            scripts/harden_race_canon.py \\\n')
        text = text.replace('            tests/test_skill_inheritance_hardening.py \\\n', '            tests/test_skill_inheritance_hardening.py \\\n            tests/test_race_hardening.py \\\n            tests/test_review_gate_idempotence.py \\\n')
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

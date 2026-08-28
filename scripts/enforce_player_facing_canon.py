from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]

BRAND_EXCLUSIONS = [
    "ウマ娘 プリティーダービー",
    "ウマ娘Pretty Derby",
    "ウマ娘 Pretty Derby",
    "赛马娘 Pretty Derby",
    "赛马娘Pretty Derby",
]


NAMED_CONDITIONS = [
    {
        "id": "condition.night_owl",
        "ja": ["夜ふかし気味"],
        "zh_cn": ["熬夜"],
        "target": "Night Owl",
        "forbidden": ["Thức khuya"],
        "note": "Named negative Condition. Current Global/community name: Night Owl. The plain zh-CN alias is valid only as the exact Condition label in text_data category 142.",
    },
    {
        "id": "condition.slacker",
        "ja": ["なまけ癖"],
        "zh_cn": ["懒惰成性"],
        "target": "Slacker",
        "forbidden": ["Lười biếng thành tính"],
        "note": "Named negative Condition; established Global name Slacker.",
    },
    {
        "id": "condition.skin_outbreak",
        "ja": ["肌荒れ"],
        "zh_cn": ["皮肤粗糙"],
        "target": "Skin Outbreak",
        "forbidden": ["Da thô ráp"],
        "note": "Named negative Condition; established Global name Skin Outbreak.",
    },
    {
        "id": "condition.slow_metabolism",
        "ja": ["太り気味"],
        "zh_cn": ["变胖"],
        "target": "Slow Metabolism",
        "forbidden": ["Tăng cân"],
        "note": "Named negative Condition; established Global name Slow Metabolism.",
    },
    {
        "id": "condition.migraine",
        "ja": ["片頭痛"],
        "zh_cn": ["偏头痛"],
        "target": "Migraine",
        "forbidden": ["Đau nửa đầu"],
        "note": "Named negative Condition; established Global name Migraine.",
    },
    {
        "id": "condition.practice_poor",
        "ja": ["練習ベタ"],
        "zh_cn": ["不擅长练习"],
        "target": "Practice Poor",
        "forbidden": ["Không giỏi luyện tập", "Poor Practice"],
        "note": "Named negative Condition. Use current Global name Practice Poor, not the older community ordering Poor Practice.",
    },
    {
        "id": "condition.fast_learner",
        "ja": ["切れ者"],
        "zh_cn": ["能人"],
        "target": "Fast Learner",
        "forbidden": ["Người tài"],
        "note": "Named positive Condition; established Global name Fast Learner.",
    },
    {
        "id": "condition.charming_circle",
        "ja": ["愛嬌○"],
        "zh_cn": ["惹人怜爱○"],
        "target": "Charming ○",
        "forbidden": ["Đáng yêu○", "Đáng yêu ○"],
        "note": "Named positive Condition; established Global name Charming ○.",
    },
    {
        "id": "condition.hot_topic",
        "ja": ["注目株"],
        "zh_cn": ["潜力股"],
        "target": "Hot Topic",
        "forbidden": ["Ngôi sao tiềm năng"],
        "note": "Named positive Condition; established Global name Hot Topic.",
    },
    {
        "id": "condition.practice_perfect_circle",
        "ja": ["練習上手○"],
        "zh_cn": ["擅长练习○"],
        "target": "Practice Perfect ○",
        "forbidden": ["Thành thạo luyện tập○", "Thành thạo luyện tập ○"],
        "note": "Named positive Condition; established Global name Practice Perfect ○.",
    },
    {
        "id": "condition.practice_perfect_double_circle",
        "ja": ["練習上手◎"],
        "zh_cn": ["擅长练习◎"],
        "target": "Practice Perfect ◎",
        "forbidden": ["Thành thạo luyện tập◎", "Thành thạo luyện tập ◎"],
        "note": "Named positive Condition; established Global name Practice Perfect ◎.",
    },
    {
        "id": "condition.under_the_weather",
        "ja": ["小さなほころび"],
        "zh_cn": ["微小的破绽"],
        "target": "Under the Weather",
        "forbidden": ["Kẽ hở nhỏ", "Cracking"],
        "note": "Super Creek named negative Condition. Current Global/community name is Under the Weather; supersedes older community label Cracking.",
    },
    {
        "id": "condition.shining_brightly",
        "ja": ["大輪の輝き"],
        "zh_cn": ["夺目的光辉"],
        "target": "Shining Brightly",
        "forbidden": ["Ánh hào quang chói lọi"],
        "note": "Super Creek named positive Condition; established Global name Shining Brightly.",
    },
    {
        "id": "condition.not_ready",
        "ja": ["まだまだ準備中"],
        "zh_cn": ["仍在准备中"],
        "target": "Not Ready",
        "forbidden": ["Vẫn đang chuẩn bị"],
        "note": "Meisho Doto named negative Condition; current established Global/community name Not Ready.",
    },
    {
        "id": "condition.legs_of_glass",
        "ja": ["ガラスの脚"],
        "zh_cn": ["玻璃般的双脚"],
        "target": "Legs of Glass",
        "forbidden": ["Đôi chân mong manh như thủy tinh"],
        "note": "Mejiro Ardan named Condition; established international/community name Legs of Glass.",
    },
    {
        "id": "condition.fan_promise",
        "ja": [
            "ファンとの約束・北海道", "ファンとの約束・北東", "ファンとの約束・中山",
            "ファンとの約束・関西", "ファンとの約束・小倉", "ファンとの約束・川崎",
        ],
        "zh_cn": [
            "与粉丝的约定・北海道", "与粉丝的约定・东北", "与粉丝的约定・中山",
            "与粉丝的约定・关西", "与粉丝的约定・小仓", "与粉丝的约定・川崎",
        ],
        "target": "Fan Promise",
        "forbidden": ["Lời hứa với fan"],
        "note": "Smart Falcon Condition family. Require the established Fan Promise concept while preserving the region; punctuation/region spelling may be resolved by the reviewer from the exact label.",
    },
]

MOOD_LEVELS = [
    {"id": "state.mood.awful", "ja": ["絶不調"], "zh_cn": ["绝不调"], "key": "Race0630", "target": "Awful", "forbidden": ["Rất tệ"]},
    {"id": "state.mood.bad", "ja": ["不調"], "zh_cn": ["不调"], "key": "Race0631", "target": "Bad", "forbidden": ["Tệ"]},
    {"id": "state.mood.normal", "ja": ["普通"], "zh_cn": ["普通"], "key": "Race0632", "target": "Normal", "forbidden": ["Bình thường"]},
    {"id": "state.mood.good", "ja": ["好調"], "zh_cn": ["好调"], "key": "Race0633", "target": "Good", "forbidden": ["Tốt"]},
    {"id": "state.mood.great", "ja": ["絶好調"], "zh_cn": ["绝好调"], "key": "Race0634", "target": "Great", "forbidden": ["Rất tốt"]},
]

CONDITION_CONTEXT = {
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [["142"]],
    "match_mode": "exact",
}

def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def upsert_by_id(items: list[dict[str, Any]], record: dict[str, Any]) -> None:
    record_id = str(record["id"])
    for index, item in enumerate(items):
        if isinstance(item, dict) and str(item.get("id", "")) == record_id:
            merged = dict(item)
            merged.update(record)
            items[index] = merged
            return
    items.append(record)


def update_registry(repo_root: Path) -> bool:
    path = repo_root / "glossary/term_registry.json"
    payload = load_json(path, {"schema_version": 2, "policy": {}, "terms": []})
    before = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    terms = payload.setdefault("terms", [])

    updates: dict[str, dict[str, Any]] = {
        "world.umamusume": {
            "target_vi": "Mã Nương",
            "exclude_source_contains": BRAND_EXCLUSIONS,
            "note": "Generic world/species term. Use Mã Nương in Vietnamese prose/dialogue; preserve the product brand Umamusume: Pretty Derby when the full title is present.",
        },
        "system.support_card": {
            "target_vi": "Support Card",
            "note": "Player-facing term; keep Support Card in English.",
        },
        "stat.speed": {"target_vi": "Speed"},
        "stat.stamina": {"target_vi": "Stamina"},
        "stat.power": {"target_vi": "Power"},
        "stat.guts": {"target_vi": "Guts"},
        "stat.wisdom": {"target_vi": "Wit"},
        "state.motivation": {
            "target_vi": "Mood",
            "note": "Player-facing state term; やる気/干劲 maps to Mood.",
        },
        "skill.generic": {"target_vi": "Skill"},
        "skill.unique": {"target_vi": "Unique Skill"},
        "skill.evolution": {"target_vi": "Evolution Skill"},
        "surface.turf": {"target_vi": "Turf"},
        "surface.dirt": {"target_vi": "Dirt"},
        "distance.sprint": {"target_vi": "Sprint"},
        "distance.mile": {"target_vi": "Mile"},
        "distance.medium": {"target_vi": "Medium"},
        "distance.long": {"target_vi": "Long"},
        "style.generic": {"target_vi": "Style"},
        "style.nige": {"target_vi": "Front Runner"},
        "style.senko": {"target_vi": "Pace Chaser"},
        "style.sashi": {"target_vi": "Late Surger"},
        "style.oikomi": {"target_vi": "End Closer"},
        "style.dai_nige": {
            "target_vi": "Runaway",
            "zh_cn": ["大逃", "爆领"],
            "note": "Player-facing English strategy name for 大逃げ; do not calque as Đại đào thoát or keep Dai Nige.",
        },
    }

    for item in terms:
        if not isinstance(item, dict):
            continue
        term_id = str(item.get("id", ""))
        if term_id in updates:
            item.update(updates[term_id])

    additions = [
        {
            "id": "world.umamusume_brand",
            "category": "world_brand",
            "ja": ["ウマ娘 プリティーダービー", "ウマ娘 Pretty Derby", "ウマ娘Pretty Derby"],
            "zh_cn": ["赛马娘 Pretty Derby", "赛马娘Pretty Derby"],
            "target_vi": "Umamusume: Pretty Derby",
            "locked": True,
            "note": "Product/franchise title. Preserve the brand; this is the explicit exception to generic ウマ娘/赛马娘 → Mã Nương.",
        },
        {
            "id": "resource.skill_pt",
            "category": "resource",
            "ja": ["スキルPt", "スキルポイント"],
            "zh_cn": ["技能Pt", "技能点", "技能点数"],
            "target_vi": "Skill Pt",
            "locked": True,
            "note": "Player-facing Skill Point resource. In prose, Skill Points is also acceptable through the community-term layer; never use Điểm kỹ năng/Pt kỹ năng.",
        },
        {
            "id": "skill.hint",
            "category": "skill",
            "ja": ["スキルヒント"],
            "zh_cn": ["技能灵感", "技能提示"],
            "target_vi": "Skill Hint",
            "locked": True,
            "note": "Player-facing term for a skill hint; do not literalize as Gợi ý Skill/Gợi ý kỹ năng.",
        },
        {
            "id": "legacy.spark",
            "category": "legacy",
            "ja": ["因子"],
            "zh_cn": ["因子"],
            "target_vi": "Spark",
            "locked": True,
            "note": "Inheritance/Legacy system term. Use Spark/Sparks rather than Nhân tố.",
        },
        {
            "id": "condition.night_owl",
            "category": "condition",
            "ja": ["夜ふかし気味"],
            "zh_cn": ["「熬夜」", "熬夜状态"],
            "target_vi": "Night Owl",
            "locked": True,
            "note": "Named Condition. Do not translate the condition label as Thức khuya; ordinary prose about staying up late is not covered by this rule.",
        },
    ]
    for record in additions:
        upsert_by_id(terms, record)

    for spec in NAMED_CONDITIONS:
        upsert_by_id(terms, {
            "id": spec["id"],
            "category": "condition",
            "ja": spec["ja"],
            "zh_cn": spec["zh_cn"],
            "target_vi": spec["target"],
            "locked": True,
            "note": spec["note"],
            **CONDITION_CONTEXT,
        })
    for spec in MOOD_LEVELS:
        upsert_by_id(terms, {
            "id": spec["id"],
            "category": "mood_level",
            "ja": spec["ja"],
            "zh_cn": spec["zh_cn"],
            "target_vi": spec["target"],
            "locked": True,
            "note": "Named Mood level; use established Global player-facing label.",
            "invalidation_scope": "item",
            "source_paths": ["localize_dict.json"],
            "key_exact": [spec["key"]],
            "match_mode": "exact",
        })

    policy = payload.setdefault("policy", {})
    policy["player_facing_rule"] = (
        "For established gameplay concepts use the canonical player-facing English/Romanized term; "
        "generic ウマ娘/赛马娘 is Mã Nương in Vietnamese, while the full product brand remains Umamusume: Pretty Derby."
    )
    policy["canonical_sync"] = "scripts/enforce_player_facing_canon.py"

    after = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    if after != before:
        write_json(path, payload)
        return True
    return False


def community_record(
    term_id: str,
    category: str,
    aliases: list[str],
    preferred: str,
    forbidden: list[str],
    *,
    accepted: list[str] | None = None,
    compact: list[str] | None = None,
    basis: str,
    exclude_source_contains: list[str] | None = None,
) -> dict[str, Any]:
    record: dict[str, Any] = {
        "id": term_id,
        "category": category,
        "source_aliases": aliases,
        "preferred": preferred,
        "compact": compact or [],
        "accepted": accepted or [preferred],
        "forbidden": forbidden,
        "require_accepted": True,
        "basis": basis,
    }
    if exclude_source_contains:
        record["exclude_source_contains"] = exclude_source_contains
    return record


def update_community(repo_root: Path) -> bool:
    path = repo_root / "glossary/ui_community_terms.json"
    payload = load_json(path, {"schema_version": 1, "policy_version": 1, "terms": []})
    before = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    payload["policy_version"] = max(int(payload.get("policy_version", 0)), 6)
    terms = payload.setdefault("terms", [])

    records = [
        community_record(
            "common.world.umamusume",
            "world",
            ["ウマ娘", "赛马娘"],
            "Mã Nương",
            ["Uma Musume"],
            basis="Vietnamese project term established by the official Vietnamese anime subtitle usage supplied by the project owner; applies to the generic world/species term, not the franchise title.",
            exclude_source_contains=BRAND_EXCLUSIONS,
        ),
        community_record(
            "common.skill_points",
            "resource",
            ["スキルPt", "スキルポイント", "技能Pt", "技能点", "技能点数"],
            "Skill Pt",
            ["Điểm kỹ năng", "Pt kỹ năng"],
            accepted=["Skill Pt", "Skill Pts", "Skill Points"],
            basis="Established player-facing terminology; UI may use Skill Pt while prose may use Skill Points.",
        ),
        community_record(
            "common.skill_hint",
            "skill",
            ["スキルヒント", "技能灵感", "技能提示"],
            "Skill Hint",
            ["Gợi ý Skill", "Gợi ý kỹ năng"],
            accepted=["Skill Hint", "Skill Hints"],
            basis="Established player-facing terminology for skill hints.",
        ),
        community_record(
            "common.spark",
            "legacy",
            ["因子"],
            "Spark",
            ["Nhân tố"],
            accepted=["Spark", "Sparks"],
            basis="Established Legacy/Inheritance terminology; Sparks pass stats, aptitudes, and Skill Hints.",
        ),
        community_record(
            "common.style.runaway",
            "running_style",
            ["大逃げ", "大逃", "爆领"],
            "Runaway",
            ["Dai Nige", "Đại đào thoát"],
            basis="Established English name for the special 大逃げ strategy.",
        ),
        community_record(
            "common.condition.night_owl",
            "condition",
            ["夜ふかし気味", "「熬夜」", "熬夜状态"],
            "Night Owl",
            ["Thức khuya"],
            basis="Named negative Condition; ordinary prose about staying up late is outside this rule.",
        ),
    ]
    for spec in NAMED_CONDITIONS:
        records.append({
            "id": "common." + spec["id"],
            "category": "condition",
            "source_aliases": spec["zh_cn"],
            "preferred": spec["target"],
            "compact": [],
            "accepted": [spec["target"]],
            "forbidden": spec["forbidden"],
            "require_accepted": True,
            "basis": spec["note"],
            **CONDITION_CONTEXT,
        })
    for spec in MOOD_LEVELS:
        records.append({
            "id": "common." + spec["id"],
            "category": "mood_level",
            "source_aliases": spec["zh_cn"],
            "preferred": spec["target"],
            "compact": [],
            "accepted": [spec["target"]],
            "forbidden": spec["forbidden"],
            "require_accepted": True,
            "basis": "Named Mood level; established Global player-facing label.",
            "invalidation_scope": "item",
            "source_paths": ["localize_dict.json"],
            "key_exact": [spec["key"]],
            "match_mode": "exact",
        })

    for record in records:
        upsert_by_id(terms, record)

    rules = payload.setdefault("rules", [])
    additions = [
        "Generic ウマ娘/赛马娘 uses Mã Nương in Vietnamese prose/dialogue; preserve Umamusume: Pretty Derby when the full product title is present.",
        "Named Conditions use their established English player-facing names; do not translate condition labels literally from zh-CN.",
        "Skill Pt, Skill Hint, Spark/Sparks, and running-style names are canonical gameplay vocabulary and must not be Vietnamese calques.",
    ]
    for rule in additions:
        if rule not in rules:
            rules.append(rule)

    after = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    if after != before:
        write_json(path, payload)
        return True
    return False



def update_source_bridge(repo_root: Path) -> bool:
    path = repo_root / "glossary/source_bridge_terms.json"
    payload = load_json(path, {"schema_version": 1, "policy": {}, "terms": [], "untrusted_sources": []})
    before = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    terms = payload.setdefault("terms", [])

    for spec in NAMED_CONDITIONS:
        upsert_by_id(terms, {
            "id": spec["id"],
            "ja": spec["ja"],
            "zh_cn": spec["zh_cn"],
            "preferred": spec["target"],
            "accepted": [spec["target"]],
            "forbidden": spec["forbidden"],
            "require_accepted": True,
            "source_paths": ["text_data_dict.json"],
            "json_path_prefixes": [["142"]],
            "match_mode": "exact",
            "note": spec["note"] + " The zh-CN semantic label is not authoritative outside this guarded Condition slot.",
        })
    for spec in MOOD_LEVELS:
        upsert_by_id(terms, {
            "id": spec["id"],
            "ja": spec["ja"],
            "zh_cn": spec["zh_cn"],
            "preferred": spec["target"],
            "accepted": [spec["target"]],
            "forbidden": spec["forbidden"],
            "require_accepted": True,
            "source_paths": ["localize_dict.json"],
            "key_exact": [spec["key"]],
            "match_mode": "exact",
            "note": "Named Mood level. Guard by exact Race0630-Race0634 UI identity so generic prose is not rewritten.",
        })

    after = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    if after != before:
        write_json(path, payload)
        return True
    return False


def ensure_audit_policy(repo_root: Path) -> bool:
    path = repo_root / "glossary/translation_audit_policy.json"
    current = load_json(path, {})
    round_number = max(1, int(current.get("audit_round", 0) or 0))
    payload = {
        "schema_version": 1,
        "audit_round": round_number,
        "round_id": current.get("round_id") or "manual-terminology-cleanup-2026-08",
        "mode": "full_retrospective_pass",
        "scope": "all currently merged Vietnamese translations",
        "purpose": "Make repeated whole-corpus audits explicit. Changing audit_round invalidates prior review context and forces another full pass even when no other glossary file changed.",
        "required_checks": [
            "semantic correctness and natural Vietnamese",
            "player-facing terminology and named Conditions",
            "proper names, race names, song titles, and creator credits",
            "zh-CN bridge artifacts or translator-only credits absent from JP",
            "numeric/condition/comparator/structure preservation",
        ],
        "completion_policy": {
            "current_round": "The translation gate clears only after every in-scope entry is resolved for this audit round.",
            "after_game_translation_complete": "Run additional full audit rounds by incrementing audit_round. At least two clean post-completion passes are recommended before treating the localization as release-clean.",
            "new_findings": "Any newly discovered systemic terminology rule should update canonical context and start/restart a full audit round rather than patch isolated lines only.",
        },
    }
    if current != payload:
        write_json(path, payload)
        return True
    return False


def patch_review_common(repo_root: Path) -> bool:
    path = repo_root / "scripts/translation_review_common.py"
    text = path.read_text(encoding="utf-8")
    original = text

    anchor = '    "glossary/ui_community_terms.json",\n'
    addition = '    "glossary/translation_audit_policy.json",\n'
    if addition not in text:
        text = text.replace(anchor, anchor + addition)

    locked_anchor = "    for term in terms:\n        aliases = [str(v) for v in term.get(\"zh_cn\", []) if str(v)]\n"
    locked_replacement = (
        "    for term in terms:\n"
        "        exclusions = [str(v) for v in term.get(\"exclude_source_contains\", []) if str(v)]\n"
        "        if exclusions and any(value in source for value in exclusions):\n"
        "            continue\n"
        "        aliases = [str(v) for v in term.get(\"zh_cn\", []) if str(v)]\n"
    )
    if locked_anchor in text:
        text = text.replace(locked_anchor, locked_replacement, 1)

    community_anchor = (
        "    for term in terms:\n"
        "        prefixes = [str(v) for v in term.get(\"key_prefixes\", []) if str(v)]\n"
    )
    community_replacement = (
        "    for term in terms:\n"
        "        exclusions = [str(v) for v in term.get(\"exclude_source_contains\", []) if str(v)]\n"
        "        if exclusions and any(value in source for value in exclusions):\n"
        "            continue\n"
        "        prefixes = [str(v) for v in term.get(\"key_prefixes\", []) if str(v)]\n"
    )
    if community_anchor in text:
        text = text.replace(community_anchor, community_replacement, 1)

    if text != original:
        path.write_text(text, encoding="utf-8", newline="\n")
        return True
    return False


def patch_translation_guard(repo_root: Path) -> bool:
    path = repo_root / "src/hachimi_tl_vi/translation_guard.py"
    text = path.read_text(encoding="utf-8")
    original = text

    community_anchor = (
        "        for term in self.community.get(\"terms\", []):\n"
        "            if not isinstance(term, dict):\n"
        "                continue\n"
        "            prefixes = _strings(term.get(\"key_prefixes\"))\n"
    )
    community_replacement = (
        "        for term in self.community.get(\"terms\", []):\n"
        "            if not isinstance(term, dict):\n"
        "                continue\n"
        "            exclusions = _strings(term.get(\"exclude_source_contains\"))\n"
        "            if exclusions and any(value in source for value in exclusions):\n"
        "                continue\n"
        "            prefixes = _strings(term.get(\"key_prefixes\"))\n"
    )
    if community_anchor in text:
        text = text.replace(community_anchor, community_replacement, 1)

    registry_anchor = (
        "        for term in self.term_registry.get(\"terms\", []):\n"
        "            if not isinstance(term, dict) or not bool(term.get(\"locked\")):\n"
        "                continue\n"
        "            expected = str(term.get(\"target_vi\", \"\")).strip()\n"
    )
    registry_replacement = (
        "        for term in self.term_registry.get(\"terms\", []):\n"
        "            if not isinstance(term, dict) or not bool(term.get(\"locked\")):\n"
        "                continue\n"
        "            exclusions = _strings(term.get(\"exclude_source_contains\"))\n"
        "            if exclusions and any(value in source for value in exclusions):\n"
        "                continue\n"
        "            expected = str(term.get(\"target_vi\", \"\")).strip()\n"
    )
    if registry_anchor in text:
        text = text.replace(registry_anchor, registry_replacement, 1)

    if text != original:
        path.write_text(text, encoding="utf-8", newline="\n")
        return True
    return False


def patch_categories(repo_root: Path) -> bool:
    path = repo_root / "src/hachimi_tl_vi/context_categories.py"
    text = path.read_text(encoding="utf-8")
    original = text
    additions = {
        '    "13": "gacha_banner_text",\n': '    "4": "trainee_card_full_name",\n',
        '    "16": "song_name",\n': '    "13": "gacha_banner_text",\n',
        '    "17": "song_credit",\n': '    "16": "song_name",\n',
        '    "128": "song_description",\n': '    "78": "support_display_name",\n',
        '    "131": "mission_objective",\n': '    "128": "song_description",\n',
        '    "171": "character_system_trigger",\n': '    "170": "character_display_name",\n',
        '    "172": "inheritance_description",\n': '    "171": "character_system_trigger",\n',
    }
    for addition, after in additions.items():
        if addition not in text and after in text:
            text = text.replace(after, after + addition, 1)
    if text != original:
        path.write_text(text, encoding="utf-8", newline="\n")
        return True
    return False


def patch_review_protocol(repo_root: Path) -> bool:
    path = repo_root / "TRANSLATION_REVIEW.md"
    text = path.read_text(encoding="utf-8")
    marker = "## Manual-audit canonical rules"
    if marker in text:
        return False
    section = r'''

## Manual-audit canonical rules

`glossary/translation_audit_policy.json` defines the explicit full-corpus audit round. It is part of the global review context hash. Incrementing `audit_round` intentionally reopens every currently merged translation, even if all other glossary files are unchanged. A cleared gate means only that the **current audit round** is clean; it is not a permanent assertion that future audits can find nothing else.

Apply these project-owner audit decisions as hard review policy:

- generic `ウマ娘` / `赛马娘` in world/prose/dialogue is **Mã Nương**; preserve the product/franchise title **Umamusume: Pretty Derby** when the full title is present;
- established gameplay vocabulary stays player-facing: **Support Card, Mood, Speed, Stamina, Power, Guts, Wit, Skill, Skill Pt/Skill Points, Skill Hint, Spark/Sparks, Turf, Dirt, Sprint, Mile, Medium, Long, Front Runner, Pace Chaser, Late Surger, End Closer, Runaway**;
- named Conditions use their established English names (for example `夜ふかし気味` / quoted `熬夜` condition → **Night Owl**). Do not replace ordinary prose containing similar words with a Condition name;
- individual Skill names still follow the Vietnamese Skill-title style/canonical registry; the keep-English rule above applies to generic gameplay labels, not every Skill title;
- song titles and race names are proper names: use the verified international/official Romanized or English form, never a literal zh-CN semantic calque. If the international form is not established in repository evidence, verify it or `defer`;
- song/person credits must use a verified Latin/Roman spelling for real creator names. CJK creator names left verbatim are not considered a clean Vietnamese result merely because the credit label was translated;
- zh-CN-only translator/editor credits such as `译：...` are bridge metadata, not automatically original game credits. If the corresponding JP source/official credit cannot confirm them, remove them when evidence is clear or `defer` instead of propagating the bridge artifact;
- `text_data` category `171` is interaction/login trigger metadata. Translate it as a condition/trigger label (for example “Khi đăng nhập buổi sáng”) rather than mistaking it for normal dialogue or an imperative UI action;
- `text_data` category `172` is inheritance/Spark description context. Literal `因子 → Nhân tố`, `技能Pt → điểm/Pt kỹ năng`, or `技能灵感 → Gợi ý Skill` is noncanonical;
- a terminology rule discovered by manual audit must be fixed in canonical context first. Do not patch only the sampled line and leave the same wrong mapping reusable elsewhere.

After the game reaches full translation, start additional whole-corpus audit rounds by incrementing `audit_round`. Multiple clean passes are expected because later context, newly translated content, and manual sampling can expose systemic errors that an earlier pass could not see.
'''
    path.write_text(text.rstrip() + section + "\n", encoding="utf-8", newline="\n")
    return True


def main() -> int:
    changed = {
        "term_registry": update_registry(REPO_ROOT),
        "ui_community_terms": update_community(REPO_ROOT),
        "source_bridge_terms": update_source_bridge(REPO_ROOT),
        "translation_audit_policy": ensure_audit_policy(REPO_ROOT),
        "translation_review_common": patch_review_common(REPO_ROOT),
        "translation_guard": patch_translation_guard(REPO_ROOT),
        "context_categories": patch_categories(REPO_ROOT),
        "translation_review_protocol": patch_review_protocol(REPO_ROOT),
    }
    print(json.dumps(changed, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

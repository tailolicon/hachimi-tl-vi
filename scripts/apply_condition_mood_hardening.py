from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def write(rel: str, text: str) -> None:
    (ROOT / rel).write_text(text, encoding="utf-8", newline="\n")


def replace_once(rel: str, old: str, new: str) -> None:
    text = read(rel)
    if old not in text:
        raise RuntimeError(f"anchor missing in {rel}: {old[:120]!r}")
    write(rel, text.replace(old, new, 1))


def regex_once(rel: str, pattern: str, replacement: str) -> None:
    text = read(rel)
    updated, count = re.subn(pattern, lambda _match: replacement, text, count=1, flags=re.S)
    if count != 1:
        raise RuntimeError(f"regex anchor count={count} in {rel}: {pattern[:120]!r}")
    write(rel, updated)


CONSTANTS = r'''NAMED_CONDITIONS = [
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

'''

replace_once(
    "scripts/enforce_player_facing_canon.py",
    "BRAND_EXCLUSIONS = [\n    \"ウマ娘 プリティーダービー\",\n    \"ウマ娘Pretty Derby\",\n    \"ウマ娘 Pretty Derby\",\n    \"赛马娘 Pretty Derby\",\n    \"赛马娘Pretty Derby\",\n]\n\n\ndef load_json",
    "BRAND_EXCLUSIONS = [\n    \"ウマ娘 プリティーダービー\",\n    \"ウマ娘Pretty Derby\",\n    \"ウマ娘 Pretty Derby\",\n    \"赛马娘 Pretty Derby\",\n    \"赛马娘Pretty Derby\",\n]\n\n\n" + CONSTANTS + "def load_json",
)

replace_once(
    "scripts/enforce_player_facing_canon.py",
    "    for record in additions:\n        upsert_by_id(terms, record)\n\n    policy = payload.setdefault(\"policy\", {})",
    '''    for record in additions:\n        upsert_by_id(terms, record)\n\n    for spec in NAMED_CONDITIONS:\n        upsert_by_id(terms, {\n            "id": spec["id"],\n            "category": "condition",\n            "ja": spec["ja"],\n            "zh_cn": spec["zh_cn"],\n            "target_vi": spec["target"],\n            "locked": True,\n            "note": spec["note"],\n            **CONDITION_CONTEXT,\n        })\n    for spec in MOOD_LEVELS:\n        upsert_by_id(terms, {\n            "id": spec["id"],\n            "category": "mood_level",\n            "ja": spec["ja"],\n            "zh_cn": spec["zh_cn"],\n            "target_vi": spec["target"],\n            "locked": True,\n            "note": "Named Mood level; use established Global player-facing label.",\n            "invalidation_scope": "item",\n            "source_paths": ["localize_dict.json"],\n            "key_exact": [spec["key"]],\n            "match_mode": "exact",\n        })\n\n    policy = payload.setdefault("policy", {})''',
)

replace_once(
    "scripts/enforce_player_facing_canon.py",
    "    for record in records:\n        upsert_by_id(terms, record)\n\n    rules = payload.setdefault(\"rules\", [])",
    '''    for spec in NAMED_CONDITIONS:\n        records.append({\n            "id": "common." + spec["id"],\n            "category": "condition",\n            "source_aliases": spec["zh_cn"],\n            "preferred": spec["target"],\n            "compact": [],\n            "accepted": [spec["target"]],\n            "forbidden": spec["forbidden"],\n            "require_accepted": True,\n            "basis": spec["note"],\n            **CONDITION_CONTEXT,\n        })\n    for spec in MOOD_LEVELS:\n        records.append({\n            "id": "common." + spec["id"],\n            "category": "mood_level",\n            "source_aliases": spec["zh_cn"],\n            "preferred": spec["target"],\n            "compact": [],\n            "accepted": [spec["target"]],\n            "forbidden": spec["forbidden"],\n            "require_accepted": True,\n            "basis": "Named Mood level; established Global player-facing label.",\n            "invalidation_scope": "item",\n            "source_paths": ["localize_dict.json"],\n            "key_exact": [spec["key"]],\n            "match_mode": "exact",\n        })\n\n    for record in records:\n        upsert_by_id(terms, record)\n\n    rules = payload.setdefault("rules", [])''',
)

SOURCE_BRIDGE_FN = r'''
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


'''
replace_once(
    "scripts/enforce_player_facing_canon.py",
    "\ndef ensure_audit_policy(repo_root: Path) -> bool:\n",
    "\n" + SOURCE_BRIDGE_FN + "def ensure_audit_policy(repo_root: Path) -> bool:\n",
)
replace_once(
    "scripts/enforce_player_facing_canon.py",
    '        "ui_community_terms": update_community(REPO_ROOT),\n        "translation_audit_policy": ensure_audit_policy(REPO_ROOT),',
    '        "ui_community_terms": update_community(REPO_ROOT),\n        "source_bridge_terms": update_source_bridge(REPO_ROOT),\n        "translation_audit_policy": ensure_audit_policy(REPO_ROOT),',
)

CONTEXT_HASH_BLOCK = r'''def _global_context_bytes(rel: str, path: Path) -> bytes:
    if rel not in {"glossary/term_registry.json", "glossary/ui_community_terms.json"}:
        return path.read_bytes()
    payload = load_json(path, {}) or {}
    if not isinstance(payload, dict):
        return path.read_bytes()
    semantic = dict(payload)
    semantic["terms"] = [
        term for term in payload.get("terms", [])
        if isinstance(term, dict) and str(term.get("invalidation_scope", "global")) != "item"
    ]
    return json.dumps(semantic, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def context_snapshot_hash(repo_root: Path) -> str:
    """Hash global review policy while excluding explicitly item-scoped canon records."""
    digest = hashlib.sha256()
    for rel in CONTEXT_PATHS:
        digest.update(rel.encode("utf-8") + b"\0")
        path = repo_root / rel
        if path.exists():
            digest.update(_global_context_bytes(rel, path))
        digest.update(b"\0")
    return digest.hexdigest()


def item_scoped_policy_hash(repo_root: Path) -> str:
    semantic: dict[str, list[dict[str, Any]]] = {}
    for rel in ("glossary/term_registry.json", "glossary/ui_community_terms.json"):
        payload = load_json(repo_root / rel, {}) or {}
        terms = payload.get("terms", []) if isinstance(payload, dict) else []
        semantic[rel] = sorted(
            [
                term for term in terms
                if isinstance(term, dict) and str(term.get("invalidation_scope", "")) == "item"
            ],
            key=lambda term: str(term.get("id", "")),
        )
    encoded = json.dumps(semantic, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


'''
regex_once(
    "scripts/translation_review_common.py",
    r"def context_snapshot_hash\(repo_root: Path\) -> str:.*?(?=def source_bridge_policy_hash)",
    CONTEXT_HASH_BLOCK,
)

MATCH_HELPERS = r'''def _alias_matches(source: str, alias: str, mode: str = "contains") -> bool:
    if not alias:
        return False
    if mode == "exact":
        return source.strip() == alias.strip()
    if source == alias:
        return True
    return len(alias) >= 2 and alias in source


def _strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(item) for item in value if str(item)]
    return []


def _context_matches(
    term: dict[str, Any],
    *,
    key: str | None,
    source_path: str | None,
    json_path: list[Any] | None,
) -> bool:
    source_paths = _strings(term.get("source_paths"))
    if source_paths and (source_path is None or source_path not in source_paths):
        return False
    exact_keys = _strings(term.get("key_exact"))
    if exact_keys and (key is None or key not in exact_keys):
        return False
    prefixes = _strings(term.get("key_prefixes"))
    if prefixes and (key is None or not any(key.startswith(prefix) for prefix in prefixes)):
        return False
    raw_prefixes = term.get("json_path_prefixes", [])
    if raw_prefixes:
        if not isinstance(json_path, list):
            return False
        normalized_path = [str(value) for value in json_path]
        matched_prefix = False
        for raw in raw_prefixes:
            values = raw if isinstance(raw, list) else [raw]
            prefix = [str(value) for value in values]
            if normalized_path[: len(prefix)] == prefix:
                matched_prefix = True
                break
        if not matched_prefix:
            return False
    return True


def _matched_aliases(source: str, aliases: list[str], term: dict[str, Any]) -> list[str]:
    mode = str(term.get("match_mode", "contains"))
    return [alias for alias in aliases if _alias_matches(source, alias, mode)]


def item_scoped_context_hash(
    *,
    key: str | None,
    source: str,
    source_path: str | None,
    json_path: list[Any] | None,
    locked_terms: list[dict[str, Any]],
    community_terms: list[dict[str, Any]],
) -> str | None:
    matched: list[dict[str, Any]] = []
    for layer, terms, alias_field in (
        ("locked", locked_terms, "zh_cn"),
        ("community", community_terms, "source_aliases"),
    ):
        for term in terms:
            if str(term.get("invalidation_scope", "")) != "item":
                continue
            if not _context_matches(term, key=key, source_path=source_path, json_path=json_path):
                continue
            aliases = _strings(term.get(alias_field))
            if not _matched_aliases(source, aliases, term):
                continue
            matched.append({"layer": layer, "term": term})
    if not matched:
        return None
    matched.sort(key=lambda item: (item["layer"], str(item["term"].get("id", ""))))
    encoded = json.dumps(matched, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


'''
regex_once(
    "scripts/translation_review_common.py",
    r"def _alias_matches\(source: str, alias: str\) -> bool:.*?(?=def load_locked_terms)",
    MATCH_HELPERS,
)

LOCKED_FN = r'''def locked_term_matches(
    source: str,
    target: str,
    terms: list[dict[str, Any]],
    *,
    key: str | None = None,
    source_path: str | None = None,
    json_path: list[Any] | None = None,
) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for term in terms:
        exclusions = [str(v) for v in term.get("exclude_source_contains", []) if str(v)]
        if exclusions and any(value in source for value in exclusions):
            continue
        if not _context_matches(term, key=key, source_path=source_path, json_path=json_path):
            continue
        aliases = [str(v) for v in term.get("zh_cn", []) if str(v)]
        matched_aliases = _matched_aliases(source, aliases, term)
        if not matched_aliases:
            continue
        expected = str(term["target_vi"])
        result.append({
            "id": str(term.get("id", "")),
            "target_vi": expected,
            "matched_aliases": matched_aliases,
            "present": contains_any(target, [expected]),
        })
    return result


'''
regex_once(
    "scripts/translation_review_common.py",
    r"def locked_term_matches\(.*?(?=def load_community_terms)",
    LOCKED_FN,
)

COMMUNITY_FN = r'''def community_term_matches(
    key: str | None,
    source: str,
    target: str,
    terms: list[dict[str, Any]],
    *,
    source_path: str | None = None,
    json_path: list[Any] | None = None,
) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for term in terms:
        exclusions = [str(v) for v in term.get("exclude_source_contains", []) if str(v)]
        if exclusions and any(value in source for value in exclusions):
            continue
        if not _context_matches(term, key=key, source_path=source_path, json_path=json_path):
            continue
        aliases = [str(v) for v in term.get("source_aliases", []) if str(v)]
        matched_aliases = _matched_aliases(source, aliases, term)
        if not matched_aliases:
            continue
        accepted = list(dict.fromkeys(
            [str(v) for v in term.get("accepted", []) if str(v)]
            + [str(v) for v in term.get("compact", []) if str(v)]
        ))
        forbidden = [str(v) for v in term.get("forbidden", []) if str(v)]
        result.append({
            "id": str(term.get("id", "")),
            "preferred": str(term.get("preferred", "")),
            "accepted": accepted,
            "forbidden": forbidden,
            "matched_aliases": matched_aliases,
            "accepted_present": contains_any(target, accepted),
            "forbidden_present": contains_any(target, forbidden),
            "require_accepted": bool(term.get("require_accepted", True)),
            "basis": str(term.get("basis", "")),
        })
    return result


'''
regex_once(
    "scripts/translation_review_common.py",
    r"def community_term_matches\(.*?(?=def load_source_bridge_config)",
    COMMUNITY_FN,
)

BRIDGE_FN = r'''def source_bridge_term_matches(
    source: str,
    target: str,
    terms: list[dict[str, Any]],
    *,
    key: str | None = None,
    source_path: str | None = None,
    json_path: list[Any] | None = None,
) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for term in terms:
        if not isinstance(term, dict):
            continue
        if not _context_matches(term, key=key, source_path=source_path, json_path=json_path):
            continue
        aliases = [str(v) for v in term.get("zh_cn", []) if str(v)]
        matched_aliases = _matched_aliases(source, aliases, term)
        if not matched_aliases:
            continue
        accepted = [str(v) for v in term.get("accepted", []) if str(v)]
        forbidden = [str(v) for v in term.get("forbidden", []) if str(v)]
        result.append({
            "id": str(term.get("id", "")),
            "preferred": str(term.get("preferred", "")),
            "accepted": accepted,
            "forbidden": forbidden,
            "matched_aliases": matched_aliases,
            "accepted_present": contains_any(target, accepted),
            "forbidden_present": contains_any(target, forbidden),
            "require_accepted": bool(term.get("require_accepted", True)),
            "ja": [str(v) for v in term.get("ja", []) if str(v)],
            "note": str(term.get("note", "")),
        })
    return result


'''
regex_once(
    "scripts/translation_review_common.py",
    r"def source_bridge_term_matches\(.*?(?=def source_bridge_risk_matches)",
    BRIDGE_FN,
)

# Build-plan integration: per-item canonical hash and structured source context.
text = read("scripts/build_translation_review_plan.py")
text = text.replace("        context_snapshot_hash,\n", "        context_snapshot_hash,\n        item_scoped_context_hash,\n        item_scoped_policy_hash,\n")
text = text.replace(
    "def _active_incomplete(repo_root: Path, context_hash: str, bridge_hash: str) -> dict[str, Any] | None:",
    "def _active_incomplete(repo_root: Path, context_hash: str, bridge_hash: str, item_policy_hash: str) -> dict[str, Any] | None:",
)
text = text.replace(
    "    if str(active.get(\"source_bridge_policy_sha256\", \"\")) != bridge_hash:\n        return None\n",
    "    if str(active.get(\"source_bridge_policy_sha256\", \"\")) != bridge_hash:\n        return None\n    if str(active.get(\"item_scoped_policy_sha256\", \"\")) != item_policy_hash:\n        return None\n",
)
text = text.replace(
    "    bridge_hash: str,\n) -> bool:\n",
    "    bridge_hash: str,\n    item_context_hash: str | None = None,\n) -> bool:\n",
    1,
)
text = text.replace(
    "    if bridge_sensitive and prior.get(\"source_bridge_policy_sha256\") != bridge_hash:\n        return False\n    return True\n",
    "    if bridge_sensitive and prior.get(\"source_bridge_policy_sha256\") != bridge_hash:\n        return False\n    prior_item_context = prior.get(\"item_context_sha256\")\n    if (prior_item_context is not None or item_context_hash is not None) and prior_item_context != item_context_hash:\n        return False\n    return True\n",
)
text = text.replace(
    "    bridge_hash = source_bridge_policy_hash(repo_root)\n    active = _active_incomplete(repo_root, context_hash, bridge_hash)\n",
    "    bridge_hash = source_bridge_policy_hash(repo_root)\n    item_policy_hash = item_scoped_policy_hash(repo_root)\n    active = _active_incomplete(repo_root, context_hash, bridge_hash, item_policy_hash)\n",
)
text = text.replace(
    '            "source_bridge_policy_sha256": bridge_hash,\n        }\n',
    '            "source_bridge_policy_sha256": bridge_hash,\n            "item_scoped_policy_sha256": item_policy_hash,\n        }\n',
    1,
)
text = text.replace(
    "            community = community_term_matches(key, source, current, community_terms)\n            locked = locked_term_matches(source, current, locked_terms)\n",
    "            community = community_term_matches(\n                key, source, current, community_terms, source_path=source_file, json_path=json_path\n            )\n            locked = locked_term_matches(\n                source, current, locked_terms, key=key, source_path=source_file, json_path=json_path\n            )\n",
)
text = text.replace(
    "            bridge_terms = source_bridge_term_matches(source, current, bridge_term_rules)\n",
    "            bridge_terms = source_bridge_term_matches(\n                source, current, bridge_term_rules, key=key, source_path=source_file, json_path=json_path\n            )\n",
)
text = text.replace(
    "            bridge_sensitive = bool(bridge_terms or bridge_risks)\n\n            prior = reviewed_entries.get(uid)\n",
    "            bridge_sensitive = bool(bridge_terms or bridge_risks)\n            item_context_hash = item_scoped_context_hash(\n                key=key,\n                source=source,\n                source_path=source_file,\n                json_path=json_path,\n                locked_terms=locked_terms,\n                community_terms=community_terms,\n            )\n\n            prior = reviewed_entries.get(uid)\n",
)
text = text.replace(
    "                bridge_hash=bridge_hash,\n            ):\n",
    "                bridge_hash=bridge_hash,\n                item_context_hash=item_context_hash,\n            ):\n",
)
text = text.replace(
    '                "source_bridge_policy_sha256": bridge_hash if bridge_sensitive else None,\n',
    '                "source_bridge_policy_sha256": bridge_hash if bridge_sensitive else None,\n                "item_context_sha256": item_context_hash,\n',
)
text = text.replace(
    '        f"{source_label[:12]}-{scope_hash[:12]}-{context_hash[:10]}"\n',
    '        f"{source_label[:12]}-{scope_hash[:12]}-{context_hash[:10]}-{item_policy_hash[:10]}"\n',
)
text = text.replace(
    '            "source_bridge_policy_sha256": bridge_hash,\n            "candidate_count": 0,\n',
    '            "source_bridge_policy_sha256": bridge_hash,\n            "item_scoped_policy_sha256": item_policy_hash,\n            "candidate_count": 0,\n',
)
text = text.replace(
    '        "source_bridge_policy_sha256": bridge_hash,\n        "scope_snapshot_sha256": scope_hash,\n',
    '        "source_bridge_policy_sha256": bridge_hash,\n        "item_scoped_policy_sha256": item_policy_hash,\n        "scope_snapshot_sha256": scope_hash,\n',
)
text = text.replace(
    '        "source_bridge_policy_sha256": bridge_hash,\n    }\n',
    '        "source_bridge_policy_sha256": bridge_hash,\n        "item_scoped_policy_sha256": item_policy_hash,\n    }\n',
    1,
)
write("scripts/build_translation_review_plan.py", text)

# Merge path must reject stale embedded item-scoped canonical context and persist the item hash.
text = read("scripts/merge_translation_review.py")
text = text.replace("        context_snapshot_hash,\n", "        context_snapshot_hash,\n        item_scoped_policy_hash,\n")
text = text.replace(
    "    terms = source_bridge_term_matches(source, candidate, bridge_term_rules)\n",
    "    terms = source_bridge_term_matches(\n        source,\n        candidate,\n        bridge_term_rules,\n        key=item.get(\"key\"),\n        source_path=item.get(\"source_path\"),\n        json_path=item.get(\"json_path\"),\n    )\n",
)
text = text.replace(
    "    current_context_hash = context_snapshot_hash(repo_root)\n    bridge_hash = source_bridge_policy_hash(repo_root)\n",
    "    current_context_hash = context_snapshot_hash(repo_root)\n    current_item_policy_hash = item_scoped_policy_hash(repo_root)\n    bridge_hash = source_bridge_policy_hash(repo_root)\n",
)
old_if = '''        if (\n            int(plan.get("policy_version", 0)) != CURRENT_POLICY_VERSION\n            or str(plan.get("context_snapshot_sha256", "")) != current_context_hash\n        ):\n            reason = (\n                "legacy_policy"\n                if int(plan.get("policy_version", 0)) != CURRENT_POLICY_VERSION\n                else "review_context_changed"\n            )\n'''
new_if = '''        if (\n            int(plan.get("policy_version", 0)) != CURRENT_POLICY_VERSION\n            or str(plan.get("context_snapshot_sha256", "")) != current_context_hash\n            or str(plan.get("item_scoped_policy_sha256", "")) != current_item_policy_hash\n        ):\n            if int(plan.get("policy_version", 0)) != CURRENT_POLICY_VERSION:\n                reason = "legacy_policy"\n            elif str(plan.get("context_snapshot_sha256", "")) != current_context_hash:\n                reason = "review_context_changed"\n            else:\n                reason = "item_scoped_policy_changed"\n'''
if old_if not in text:
    raise RuntimeError("merge plan validation anchor missing")
text = text.replace(old_if, new_if, 1)
text = text.replace(
    '                "context_snapshot_sha256": current_context_hash,\n',
    '                "context_snapshot_sha256": current_context_hash,\n                "item_context_sha256": item.get("item_context_sha256"),\n                "item_scoped_policy_sha256": current_item_policy_hash,\n',
)
text = text.replace(
    '            "source_bridge_policy_sha256": bridge_hash,\n        })\n',
    '            "source_bridge_policy_sha256": bridge_hash,\n            "item_scoped_policy_sha256": current_item_policy_hash,\n        })\n',
    1,
)
write("scripts/merge_translation_review.py", text)

# Hard translation guard: honor path/category/key guards for canonical terms and bridge rules.
text = read("src/hachimi_tl_vi/translation_guard.py")
old_alias = '''def _alias_matches(source: str, alias: str) -> bool:\n    if not alias:\n        return False\n    if source == alias:\n        return True\n    return len(alias) >= 2 and alias in source\n\n\ndef _strings'''
new_alias = '''def _alias_matches(source: str, alias: str, mode: str = "contains") -> bool:\n    if not alias:\n        return False\n    if mode == "exact":\n        return source.strip() == alias.strip()\n    if source == alias:\n        return True\n    return len(alias) >= 2 and alias in source\n\n\ndef _context_matches(\n    term: dict[str, Any],\n    *,\n    key: str | None,\n    source_path: str | None,\n    json_path: list[Any] | None,\n) -> bool:\n    source_paths = _strings(term.get("source_paths"))\n    if source_paths and (source_path is None or source_path not in source_paths):\n        return False\n    exact_keys = _strings(term.get("key_exact"))\n    if exact_keys and (key is None or key not in exact_keys):\n        return False\n    prefixes = _strings(term.get("key_prefixes"))\n    if prefixes and (key is None or not any(key.startswith(prefix) for prefix in prefixes)):\n        return False\n    raw_prefixes = term.get("json_path_prefixes", [])\n    if raw_prefixes:\n        if not isinstance(json_path, list):\n            return False\n        normalized = [str(value) for value in json_path]\n        if not any(\n            normalized[: len(raw if isinstance(raw, list) else [raw])]\n            == [str(value) for value in (raw if isinstance(raw, list) else [raw])]\n            for raw in raw_prefixes\n        ):\n            return False\n    return True\n\n\ndef _strings'''
if old_alias not in text:
    raise RuntimeError("translation_guard alias anchor missing")
text = text.replace(old_alias, new_alias, 1)
text = text.replace(
    "    def _community_matches(self, source: str, key: str | None) -> list[dict[str, Any]]:\n",
    "    def _community_matches(\n        self, source: str, key: str | None, source_path: str | None, json_path: list[Any] | None\n    ) -> list[dict[str, Any]]:\n",
)
text = text.replace(
    '''            prefixes = _strings(term.get("key_prefixes"))\n            if prefixes and (key is None or not any(key.startswith(prefix) for prefix in prefixes)):\n                continue\n            aliases = _strings(term.get("source_aliases"))\n            matched = [alias for alias in aliases if _alias_matches(source, alias)]\n''',
    '''            if not _context_matches(term, key=key, source_path=source_path, json_path=json_path):\n                continue\n            aliases = _strings(term.get("source_aliases"))\n            mode = str(term.get("match_mode", "contains"))\n            matched = [alias for alias in aliases if _alias_matches(source, alias, mode)]\n''',
    1,
)
text = text.replace(
    "        key: str | None = None,\n    ) -> list[str]:\n",
    "        key: str | None = None,\n        source_path: str | None = None,\n        json_path: list[Any] | None = None,\n    ) -> list[str]:\n",
    1,
)
text = text.replace(
    "        community_matches = self._community_matches(source, key)\n",
    "        community_matches = self._community_matches(source, key, source_path, json_path)\n",
)
text = text.replace(
    '''            expected = str(term.get("target_vi", "")).strip()\n            if not expected:\n                continue\n            aliases = _strings(term.get("zh_cn"))\n            matched = [alias for alias in aliases if _alias_matches(source, alias)]\n''',
    '''            if not _context_matches(term, key=key, source_path=source_path, json_path=json_path):\n                continue\n            expected = str(term.get("target_vi", "")).strip()\n            if not expected:\n                continue\n            aliases = _strings(term.get("zh_cn"))\n            mode = str(term.get("match_mode", "contains"))\n            matched = [alias for alias in aliases if _alias_matches(source, alias, mode)]\n''',
    1,
)
text = text.replace(
    '''        for term in self.bridge.get("terms", []):\n            aliases = _strings(term.get("zh_cn"))\n            if not any(_alias_matches(source, alias) for alias in aliases):\n                continue\n''',
    '''        for term in self.bridge.get("terms", []):\n            if not _context_matches(term, key=key, source_path=source_path, json_path=json_path):\n                continue\n            aliases = _strings(term.get("zh_cn"))\n            mode = str(term.get("match_mode", "contains"))\n            if not any(_alias_matches(source, alias, mode) for alias in aliases):\n                continue\n''',
    1,
)
write("src/hachimi_tl_vi/translation_guard.py", text)

for rel in ("scripts/merge_parallel_results.py", "scripts/aggregate_parallel_results.py"):
    text = read(rel)
    old = '''                uid=str(source.get("uid", "")) or None,\n                key=_entry_key(source),\n'''
    if rel.endswith("merge_parallel_results.py"):
        old = '''                    uid=str(uid),\n                    key=_entry_key(source_entry),\n'''
        new = '''                    uid=str(uid),\n                    key=_entry_key(source_entry),\n                    source_path=str(source_entry.get("source_path", "")) or None,\n                    json_path=source_entry.get("json_path") if isinstance(source_entry.get("json_path"), list) else None,\n'''
    else:
        new = '''                uid=str(source.get("uid", "")) or None,\n                key=_entry_key(source),\n                source_path=str(source.get("source_path", "")) or None,\n                json_path=source.get("json_path") if isinstance(source.get("json_path"), list) else None,\n'''
    if old not in text:
        raise RuntimeError(f"quality guard call anchor missing in {rel}")
    write(rel, text.replace(old, new, 1))

# Regression tests for exact named-condition context, Mood-key safety, and item-scoped invalidation.
text = read("tests/test_translation_review.py")
text = text.replace(
    "    community_term_matches,\n    locked_term_matches,\n",
    "    community_term_matches,\n    context_snapshot_hash,\n    item_scoped_context_hash,\n    item_scoped_policy_hash,\n    locked_term_matches,\n",
)
text = text.replace("from scripts.merge_translation_review import _validate_result\n", "from scripts.merge_translation_review import _validate_result\nimport json\n")
append = r'''


def test_named_condition_exact_context_does_not_match_ordinary_prose():
    terms = [{
        "id": "common.condition.night_owl",
        "source_aliases": ["熬夜"],
        "preferred": "Night Owl",
        "accepted": ["Night Owl"],
        "forbidden": ["Thức khuya"],
        "require_accepted": True,
        "source_paths": ["text_data_dict.json"],
        "json_path_prefixes": [["142"]],
        "match_mode": "exact",
        "invalidation_scope": "item",
    }]
    matched = community_term_matches(
        None,
        "熬夜",
        "Thức khuya",
        terms,
        source_path="text_data_dict.json",
        json_path=["142", "1"],
    )
    assert matched and matched[0]["preferred"] == "Night Owl"
    assert community_term_matches(
        None,
        "总是会不自觉地熬夜",
        "Luôn vô thức thức khuya",
        terms,
        source_path="text_data_dict.json",
        json_path=["143", "1"],
    ) == []


def test_mood_level_requires_exact_ui_key():
    terms = [{
        "id": "common.state.mood.normal",
        "source_aliases": ["普通"],
        "preferred": "Normal",
        "accepted": ["Normal"],
        "forbidden": ["Bình thường"],
        "require_accepted": True,
        "source_paths": ["localize_dict.json"],
        "key_exact": ["Race0632"],
        "match_mode": "exact",
        "invalidation_scope": "item",
    }]
    assert community_term_matches(
        "Race0632", "普通", "Bình thường", terms,
        source_path="localize_dict.json", json_path=["Race0632"],
    )
    assert community_term_matches(
        "Menu999", "普通", "Bình thường", terms,
        source_path="localize_dict.json", json_path=["Menu999"],
    ) == []


def test_item_scoped_canon_changes_policy_hash_without_global_context_hash(tmp_path):
    glossary = tmp_path / "glossary"
    glossary.mkdir()
    (tmp_path / "TRANSLATION_REVIEW.md").write_text("review", encoding="utf-8")
    (tmp_path / "GAME_CONTEXT.md").write_text("context", encoding="utf-8")
    for name in ("translation_audit_policy.json", "skill_name_style.json", "style_rules.json"):
        (glossary / name).write_text("{}", encoding="utf-8")
    (glossary / "term_registry.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    (glossary / "ui_community_terms.json").write_text(json.dumps({"terms": []}), encoding="utf-8")
    global_before = context_snapshot_hash(tmp_path)
    scoped_before = item_scoped_policy_hash(tmp_path)
    scoped = {
        "id": "common.condition.night_owl",
        "source_aliases": ["熬夜"],
        "preferred": "Night Owl",
        "accepted": ["Night Owl"],
        "invalidation_scope": "item",
        "source_paths": ["text_data_dict.json"],
        "json_path_prefixes": [["142"]],
        "match_mode": "exact",
    }
    (glossary / "ui_community_terms.json").write_text(json.dumps({"terms": [scoped]}), encoding="utf-8")
    assert context_snapshot_hash(tmp_path) == global_before
    assert item_scoped_policy_hash(tmp_path) != scoped_before
    assert item_scoped_context_hash(
        key=None,
        source="熬夜",
        source_path="text_data_dict.json",
        json_path=["142", "1"],
        locked_terms=[],
        community_terms=[scoped],
    ) is not None
    assert item_scoped_context_hash(
        key=None,
        source="今天熬夜了",
        source_path="text_data_dict.json",
        json_path=["143", "1"],
        locked_terms=[],
        community_terms=[scoped],
    ) is None
'''
if "test_named_condition_exact_context_does_not_match_ordinary_prose" not in text:
    text = text.rstrip() + append + "\n"
write("tests/test_translation_review.py", text)

text = read("tests/test_translation_guard.py")
append = '\n\n\ndef test_guard_named_condition_is_path_scoped(tmp_path: Path) -> None:\n    guard = _guard(tmp_path)\n    guard.term_registry.setdefault("terms", []).append({\n        "id": "condition.night_owl",\n        "locked": True,\n        "zh_cn": ["熬夜"],\n        "target_vi": "Night Owl",\n        "source_paths": ["text_data_dict.json"],\n        "json_path_prefixes": [["142"]],\n        "match_mode": "exact",\n    })\n    guard.community.setdefault("terms", []).append({\n        "id": "common.condition.night_owl",\n        "source_aliases": ["熬夜"],\n        "accepted": ["Night Owl"],\n        "compact": [],\n        "forbidden": ["Thức khuya"],\n        "require_accepted": True,\n        "source_paths": ["text_data_dict.json"],\n        "json_path_prefixes": [["142"]],\n        "match_mode": "exact",\n    })\n    errors = guard.validate(\n        "熬夜",\n        "Thức khuya",\n        source_path="text_data_dict.json",\n        json_path=["142", "1"],\n    )\n    assert "community_forbidden:common.condition.night_owl" in errors\n    assert "community_required:common.condition.night_owl" in errors\n    assert guard.validate(\n        "熬夜",\n        "Night Owl",\n        source_path="text_data_dict.json",\n        json_path=["142", "1"],\n    ) == []\n    assert guard.validate(\n        "今天熬夜了",\n        "Hôm nay đã thức khuya",\n        source_path="text_data_dict.json",\n        json_path=["143", "1"],\n    ) == []\n'
if "test_guard_named_condition_is_path_scoped" not in text:
    text = text.rstrip() + append + "\n"
write("tests/test_translation_guard.py", text)
print('condition/mood hardening patch applied')

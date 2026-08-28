from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]


SPARK_ACCEPTED = ["Spark", "Sparks"]
SPARK_FORBIDDEN = ["Nhân tố", "nhân tố", "Factor", "factor"]
SKILL_PT_ACCEPTED = ["Skill Pt", "Skill Pts", "Skill Points"]
SKILL_PT_FORBIDDEN = ["Điểm kỹ năng", "điểm kỹ năng", "điểm Skill", "Pt kỹ năng"]
SKILL_HINT_ACCEPTED = ["Skill Hint", "Skill Hints"]
SKILL_HINT_FORBIDDEN = [
    "Gợi ý Skill",
    "Gợi ý kỹ năng",
    "Cảm hứng Skill",
    "Cảm hứng kỹ năng",
]


def _load(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _upsert(items: list[dict[str, Any]], record: dict[str, Any]) -> dict[str, Any]:
    record_id = str(record["id"])
    for index, item in enumerate(items):
        if isinstance(item, dict) and str(item.get("id", "")) == record_id:
            merged = dict(item)
            merged.update(record)
            items[index] = merged
            return merged
    items.append(dict(record))
    return items[-1]


def _find(items: list[dict[str, Any]], record_id: str) -> dict[str, Any] | None:
    for item in items:
        if isinstance(item, dict) and str(item.get("id", "")) == record_id:
            return item
    return None


def _dedupe(values: list[str]) -> list[str]:
    return list(dict.fromkeys(str(value) for value in values if str(value)))


def _harden_registry(repo_root: Path) -> None:
    path = repo_root / "glossary/term_registry.json"
    payload = _load(path, {"terms": []})
    terms = payload.setdefault("terms", [])

    # The old umbrella record matched every zh-CN 因子 globally. Keep the ID as
    # documentation/history, but remove it from hard matching; the mechanic is
    # reintroduced below only in observed inheritance/Spark contexts.
    umbrella = _find(terms, "legacy.spark")
    if umbrella is not None:
        umbrella["zh_cn"] = []
        umbrella["locked"] = False
        umbrella["note"] = (
            "Umbrella Spark vocabulary record only. zh-CN 因子 is intentionally not matched globally; "
            "use the item-scoped legacy.spark.* records for proven inheritance/Spark contexts."
        )

    _upsert(
        terms,
        {
            "id": "legacy.spark.inheritance_description",
            "category": "legacy",
            "ja": ["因子"],
            "zh_cn": ["因子"],
            "target_vi": "Spark",
            "locked": True,
            "source_paths": ["text_data_dict.json"],
            "json_path_prefixes": [["172"]],
            "match_mode": "contains",
            "invalidation_scope": "item",
            "note": (
                "text_data category 172 is the pinned inheritance-description table. In this category 因子 is the "
                "Uma Musume Spark mechanic (stats, aptitudes, Skill-related inheritance), not generic factor/cause prose."
            ),
        },
    )
    _upsert(
        terms,
        {
            "id": "legacy.spark.localize_ui",
            "category": "legacy",
            "ja": ["因子"],
            "zh_cn": ["因子"],
            "target_vi": "Spark",
            "locked": True,
            "source_paths": ["localize_dict.json"],
            "match_mode": "contains",
            "invalidation_scope": "item",
            "note": (
                "Current localize_dict 因子 occurrences are player-facing Spark/Legacy UI (FactorResearch, SingleMode, "
                "Outgame inheritance screens). The rule is source-path scoped so story/assets using generic factor language do not match."
            ),
        },
    )
    _upsert(
        terms,
        {
            "id": "skill.hint_level.singlemode0358",
            "category": "skill",
            "ja": ["ヒントLv"],
            "zh_cn": ["灵感等级"],
            "target_vi": "Hint Lv",
            "locked": True,
            "source_paths": ["localize_dict.json"],
            "key_exact": ["SingleMode0358"],
            "match_mode": "contains",
            "invalidation_scope": "item",
            "note": (
                "SingleMode0358 is the Skill Hint level UI. Do not generalize plain 灵感/提示 to Hint because those words "
                "also occur as ordinary inspiration/advice."
            ),
        },
    )
    _upsert(
        terms,
        {
            "id": "legacy.affinity.outgame034x",
            "category": "legacy",
            "ja": ["相性"],
            "zh_cn": ["相性"],
            "target_vi": "Affinity",
            "locked": True,
            "source_paths": ["localize_dict.json"],
            "key_exact": ["Outgame0343", "Outgame0345", "Outgame0346", "Outgame0347"],
            "match_mode": "contains",
            "invalidation_scope": "item",
            "note": (
                "These exact Legacy UI slots are the Affinity bonus/◎/〇/△ labels. Scope is deliberately narrow; ordinary "
                "compatibility prose is not forced to the English system label."
            ),
        },
    )

    _write(path, payload)


def _harden_community(repo_root: Path) -> None:
    path = repo_root / "glossary/ui_community_terms.json"
    payload = _load(path, {"terms": []})
    terms = payload.setdefault("terms", [])

    skill_pt = _find(terms, "common.skill_points")
    if skill_pt is not None:
        skill_pt["source_aliases"] = _dedupe(
            list(skill_pt.get("source_aliases", [])) + ["スキルPt", "スキルポイント", "技能Pt", "技能点", "技能点数"]
        )
        skill_pt["preferred"] = "Skill Pt"
        skill_pt["accepted"] = SKILL_PT_ACCEPTED
        skill_pt["forbidden"] = SKILL_PT_FORBIDDEN
        skill_pt["require_accepted"] = True
        skill_pt["basis"] = (
            "Established player-facing resource terminology. UI may display Skill Pt; grammatical/plural prose may use "
            "Skill Pts or Skill Points. Generic points outside the full source aliases do not match this rule."
        )

    skill_hint = _find(terms, "common.skill_hint")
    if skill_hint is not None:
        skill_hint["source_aliases"] = _dedupe(
            [alias for alias in skill_hint.get("source_aliases", []) if alias not in {"提示", "灵感", "启示"}]
            + ["スキルヒント", "技能灵感", "技能提示"]
        )
        skill_hint["preferred"] = "Skill Hint"
        skill_hint["accepted"] = SKILL_HINT_ACCEPTED
        skill_hint["forbidden"] = SKILL_HINT_FORBIDDEN
        skill_hint["require_accepted"] = True
        skill_hint["basis"] = (
            "Skill Hint is a gameplay concept. Only the full Skill-Hint compounds are canonical aliases here; bare "
            "提示/灵感/启示 remain ordinary language unless a narrower context rule proves otherwise."
        )

    umbrella = _find(terms, "common.spark")
    if umbrella is not None:
        umbrella["source_aliases"] = []
        umbrella["basis"] = (
            "Umbrella Spark vocabulary only. 因子 must not match globally because zh-CN can also use the word for a generic "
            "factor/cause. Item-scoped Spark records below carry the actual enforcement."
        )

    spark_common = {
        "preferred": "Spark",
        "accepted": SPARK_ACCEPTED,
        "compact": [],
        "forbidden": SPARK_FORBIDDEN,
        "require_accepted": True,
        "match_mode": "contains",
        "invalidation_scope": "item",
    }
    _upsert(
        terms,
        {
            "id": "common.spark.inheritance_description",
            "source_aliases": ["因子"],
            **spark_common,
            "source_paths": ["text_data_dict.json"],
            "json_path_prefixes": [["172"]],
            "basis": (
                "Pinned text_data category 172 is inheritance-description content; 因子 there is the Spark mechanic. "
                "Item scope prevents unrelated review IDs from reopening."
            ),
        },
    )
    _upsert(
        terms,
        {
            "id": "common.spark.localize_ui",
            "source_aliases": ["因子"],
            **spark_common,
            "source_paths": ["localize_dict.json"],
            "basis": (
                "Observed localize_dict occurrences are Spark/Legacy UI. Story/assets are intentionally outside this source-path guard."
            ),
        },
    )
    _upsert(
        terms,
        {
            "id": "common.skill_hint.level.singlemode0358",
            "source_aliases": ["灵感等级"],
            "preferred": "Hint Lv",
            "accepted": ["Hint Lv"],
            "compact": [],
            "forbidden": ["Lv gợi ý", "Cấp gợi ý", "Lv cảm hứng", "Cấp cảm hứng"],
            "require_accepted": True,
            "source_paths": ["localize_dict.json"],
            "key_exact": ["SingleMode0358"],
            "match_mode": "contains",
            "invalidation_scope": "item",
            "basis": (
                "Exact observed Skill Hint-level UI. Bare 灵感 is deliberately not an alias because it can mean ordinary inspiration."
            ),
        },
    )
    _upsert(
        terms,
        {
            "id": "common.legacy.affinity.outgame034x",
            "source_aliases": ["相性"],
            "preferred": "Affinity",
            "accepted": ["Affinity"],
            "compact": [],
            "forbidden": ["Tương thích"],
            "require_accepted": True,
            "source_paths": ["localize_dict.json"],
            "key_exact": ["Outgame0343", "Outgame0345", "Outgame0346", "Outgame0347"],
            "match_mode": "contains",
            "invalidation_scope": "item",
            "basis": (
                "Global Legacy UI uses Affinity for the compatibility indicator. These exact zh-CN UI keys are the bonus and "
                "◎/〇/△ Affinity labels; no global 相性 replacement is introduced."
            ),
        },
    )

    # Legacy / Guest Legacy / Inspiration are established vocabulary, but the zh-CN bridge words 继承/传承 are too broad.
    # Keep the umbrella records documentation-only until an exact source identity/key is verified.
    for record_id in ("common.legacy", "common.guest_legacy", "common.inspiration"):
        record = _find(terms, record_id)
        if record is not None:
            record["source_aliases"] = []

    _write(path, payload)


def _document_bridge_policy(repo_root: Path) -> None:
    path = repo_root / "glossary/source_bridge_terms.json"
    payload = _load(path, {"schema_version": 1, "policy": {}, "terms": [], "untrusted_sources": []})
    policy = payload.setdefault("policy", {})
    policy["skill_inheritance_hardening"] = (
        "Do not add blind source-bridge aliases for 技能点/提示/灵感/因子/继承/传承. Full Skill Pt/Skill Hint compounds and "
        "proven Spark/Affinity contexts are enforced by canonical records; bare inheritance/inspiration words remain deferred "
        "until JP identity or an exact UI key proves the player-facing concept."
    )
    _write(path, payload)


def harden(repo_root: Path = REPO_ROOT) -> None:
    _harden_registry(repo_root)
    _harden_community(repo_root)
    _document_bridge_policy(repo_root)


if __name__ == "__main__":
    harden()

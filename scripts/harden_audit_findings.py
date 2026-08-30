from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

NIGHT_OWL_REFERENCE_VARIANT = {
    "id": "common.condition.night_owl.reference_variant",
    "category": "condition",
    "source_aliases": ["熬夜倾向"],
    "preferred": "Night Owl",
    "compact": [],
    "accepted": ["Night Owl"],
    "forbidden": ["Xu hướng thức khuya", "Thức khuya"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [["143"]],
    "match_mode": "contains",
    "basis": "Named Night Owl Condition reference variant found during retrospective audit; scoped to text_data category 143 so ordinary prose about staying up late is not canonicalized.",
}

JUNIOR_MAKE_DEBUT = {
    "id": "race.junior_make_debut.singlemode619001",
    "category": "race",
    "source_aliases": ["新马级出道赛"],
    "preferred": "Junior Make Debut",
    "compact": [],
    "accepted": ["Junior Make Debut"],
    "forbidden": ["tân mã", "Tân mã", "giải ra mắt cấp Tân mã", "Giải ra mắt cấp Tân mã"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["localize_dict.json"],
    "key_exact": ["SingleMode619001"],
    "match_mode": "contains",
    "basis": "Established English player-facing name for the first Career race objective. The source alias is scoped to the proven SingleMode619001 slot so generic debut prose is unaffected.",
}

JUNIOR_MAKE_DEBUT_DECISION = {
    "decision_id": "audit.finding.junior-make-debut",
    "source_zh_cn": "新马级出道赛",
    "action": "lock",
    "target_vi": "Junior Make Debut",
    "kind": "race",
    "category": "race",
    "note": "Established player-facing English race label for the initial Career objective; canonical matching itself remains item-scoped through race.junior_make_debut.singlemode619001.",
}

MOXIE_SKILL = {
    "id": "skill.moxie.text147",
    "category": "skill_name",
    "source_aliases": ["随势而动"],
    "preferred": "Moxie",
    "compact": [],
    "accepted": ["Moxie"],
    "forbidden": ["Thuận thế hành động"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [["147"]],
    "match_mode": "exact",
    "basis": "Verified identity: zh-CN 随势而动 is JP 勢い任せ (skill IDs 2012801/2012802/2012803); the released English player-facing name is Moxie. Exact source alias plus skill-title category prevents generic prose matching.",
}

MOXIE_SKILL_DECISION = {
    "decision_id": "audit.finding.moxie",
    "source_zh_cn": "随势而动",
    "action": "lock",
    "target_vi": "Moxie",
    "kind": "skill_name",
    "category": "skill_name",
    "note": "Verified against JP 勢い任せ and released EN Moxie. Applies to the repeated text_data category-147 skill-title entries only through the scoped community rule.",
}

SCHOLAR_CONDITION = {
    "id": "condition.scholar.trainer_ability",
    "category": "condition",
    "source_aliases": ["勤勉好学"],
    "preferred": "Scholar",
    "compact": [],
    "accepted": ["Scholar"],
    "forbidden": ["Siêng năng hiếu học"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [["142"]],
    "match_mode": "exact",
    "basis": "Uma Musume JP 5.5th Anniversary Trainer Ability Condition: JP 勉強家. Current English community label Scholar; scoped to the Condition-name table so generic study/diligence prose is unaffected.",
}

MENTAL_GUARD_CONDITION = {
    "id": "condition.mental_guard.trainer_ability",
    "category": "condition",
    "source_aliases": ["精神防护"],
    "preferred": "Mental Guard",
    "compact": [],
    "accepted": ["Mental Guard"],
    "forbidden": ["Bảo vệ tinh thần"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [["142"]],
    "match_mode": "exact",
    "basis": "Uma Musume JP 5.5th Anniversary Trainer Ability Condition: JP メンタルガード. Preserve the player-facing katakana identity as Mental Guard; scope is limited to the Condition-name table.",
}

RECOVERY_SPIRIT_CONDITION = {
    "id": "condition.recovery_spirit.trainer_ability",
    "category": "condition",
    "source_aliases": ["恢复精神"],
    "preferred": "Recovery Spirit",
    "compact": [],
    "accepted": ["Recovery Spirit"],
    "forbidden": ["Hồi phục tinh thần"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [["142"]],
    "match_mode": "exact",
    "basis": "Uma Musume JP 5.5th Anniversary Trainer Ability Condition: JP リカバリー精神. Preserve the mixed English/Japanese player-facing identity as Recovery Spirit; scope is limited to the Condition-name table.",
}

EPIPHANEIA_NO_HOLDING_BACK_CONDITION = {
    "id": "condition.epiphaneia.no_holding_back",
    "category": "condition",
    "source_aliases": ["传至双腿的焦躁"],
    "preferred": "I Won't Hold Back!!",
    "compact": [],
    "accepted": ["I Won't Hold Back!!"],
    "forbidden": ["Sự nôn nóng lan xuống đôi chân"],
    "require_accepted": True,
    "invalidation_scope": "item",
    "source_paths": ["text_data_dict.json"],
    "json_path_prefixes": [["142"]],
    "match_mode": "exact",
    "basis": "Epiphaneia-specific bad Condition introduced with her JP release. Current JP guides identify アタシは抑えない！！ as the Condition that makes her slightly more prone to 掛かり; zh-CN 传至双腿的焦躁 describes that leg-borne restlessness and is distinct from the other two Epiphaneia Conditions (final-straight speed loss and Wit loss). Use a direct player-facing English rendering of the JP title until an official Global name exists; keep the rule confined to the Condition-name table.",
}

TRAINER_ABILITY_CONDITION_DECISIONS = (
    {
        "decision_id": "audit.finding.condition-scholar",
        "source_zh_cn": "勤勉好学",
        "action": "lock",
        "target_vi": "Scholar",
        "kind": "condition",
        "category": "condition",
        "note": "Verified as JP 勉強家 from the 5.5th Anniversary Trainer Ability system; use current English community label Scholar in the scoped Condition-name table.",
    },
    {
        "decision_id": "audit.finding.condition-mental-guard",
        "source_zh_cn": "精神防护",
        "action": "lock",
        "target_vi": "Mental Guard",
        "kind": "condition",
        "category": "condition",
        "note": "Verified as JP メンタルガード from the 5.5th Anniversary Trainer Ability system; preserve Mental Guard in the scoped Condition-name table.",
    },
    {
        "decision_id": "audit.finding.condition-recovery-spirit",
        "source_zh_cn": "恢复精神",
        "action": "lock",
        "target_vi": "Recovery Spirit",
        "kind": "condition",
        "category": "condition",
        "note": "Verified as JP リカバリー精神 from the 5.5th Anniversary Trainer Ability system; preserve Recovery Spirit in the scoped Condition-name table.",
    },
)

EPIPHANEIA_NO_HOLDING_BACK_DECISION = {
    "decision_id": "audit.finding.condition-epiphaneia-no-holding-back",
    "source_zh_cn": "传至双腿的焦躁",
    "action": "lock",
    "target_vi": "I Won't Hold Back!!",
    "kind": "condition",
    "category": "condition",
    "note": "Mapped to JP アタシは抑えない！！ from Epiphaneia's three release-specific bad Conditions by its unique 掛かり-prone effect; direct English rendering is used because the character is not yet released on Global.",
}


def _load(path: Path, default: dict[str, Any] | None = None) -> dict[str, Any]:
    if not path.exists():
        return dict(default or {})
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _upsert(items: list[Any], record: dict[str, Any], *, id_field: str = "id") -> None:
    record_id = str(record[id_field])
    for index, item in enumerate(items):
        if isinstance(item, dict) and str(item.get(id_field) or "") == record_id:
            merged = dict(item)
            merged.update(record)
            items[index] = merged
            return
    items.append(record)


def harden(repo_root: Path = ROOT) -> bool:
    changed = False

    community_path = repo_root / "glossary" / "ui_community_terms.json"
    community = _load(community_path, {"schema_version": 1, "terms": []})
    before = json.dumps(community, ensure_ascii=False, sort_keys=True)
    terms = community.setdefault("terms", [])
    if not isinstance(terms, list):
        raise ValueError("glossary/ui_community_terms.json terms must be a list")
    _upsert(terms, NIGHT_OWL_REFERENCE_VARIANT)
    _upsert(terms, JUNIOR_MAKE_DEBUT)
    _upsert(terms, MOXIE_SKILL)
    _upsert(terms, SCHOLAR_CONDITION)
    _upsert(terms, MENTAL_GUARD_CONDITION)
    _upsert(terms, RECOVERY_SPIRIT_CONDITION)
    _upsert(terms, EPIPHANEIA_NO_HOLDING_BACK_CONDITION)
    if before != json.dumps(community, ensure_ascii=False, sort_keys=True):
        _write(community_path, community)
        changed = True

    reviews_path = repo_root / "glossary" / "terminology_reviews.json"
    reviews = _load(reviews_path, {"schema_version": 1, "decisions": []})
    before = json.dumps(reviews, ensure_ascii=False, sort_keys=True)
    decisions = reviews.setdefault("decisions", [])
    if not isinstance(decisions, list):
        raise ValueError("glossary/terminology_reviews.json decisions must be a list")
    _upsert(decisions, JUNIOR_MAKE_DEBUT_DECISION, id_field="decision_id")
    _upsert(decisions, MOXIE_SKILL_DECISION, id_field="decision_id")
    for decision in TRAINER_ABILITY_CONDITION_DECISIONS:
        _upsert(decisions, decision, id_field="decision_id")
    _upsert(decisions, EPIPHANEIA_NO_HOLDING_BACK_DECISION, id_field="decision_id")
    if before != json.dumps(reviews, ensure_ascii=False, sort_keys=True):
        _write(reviews_path, reviews)
        changed = True

    return changed


def main() -> int:
    changed = harden(ROOT)
    print(f"audit_finding_hardening_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

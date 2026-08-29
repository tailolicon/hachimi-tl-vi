from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]

TRAINEE_SOURCE_FORMS = ["育成赛马娘", "育成\n赛马娘"]


SCOPED_UI_TERMS: tuple[dict[str, Any], ...] = (
    {
        "id": "career.ui.mode",
        "category": "career_ui",
        "ja": ["育成"],
        "zh_cn": ["育成"],
        "target_vi": "Career",
        "source_paths": ["localize_dict.json"],
        "key_exact": [
            "SingleMode0039",
            "SingleMode0526",
            "SingleMode0534",
            "SingleMode0538",
            "SingleMode194016",
            "SingleMode194020",
            "SingleModeScenarioTeamRace0033",
        ],
        "match_mode": "contains",
        "note": "These proven system/UI keys refer to Career mode. Do not globally map 育成 because compounds such as 育成ウマ娘 identify a Trainee instead.",
    },
    {
        "id": "career.ui.trainee",
        "category": "career_ui",
        "ja": ["育成ウマ娘"],
        "zh_cn": TRAINEE_SOURCE_FORMS,
        "target_vi": "Trainee",
        "source_paths": ["localize_dict.json"],
        "key_exact": ["SingleMode0038", "SingleModeScenarioMecha194090"],
        "match_mode": "contains",
        "note": "Player-facing Career selection/category concept. Treat the full compound as Trainee, distinct from generic world/species ウマ娘/赛马娘 and from bare 育成 = Career.",
    },
    {
        "id": "career.ui.goal_race",
        "category": "career_ui",
        "ja": ["目標レース"],
        "zh_cn": ["目标比赛"],
        "target_vi": "Goal Race",
        "source_paths": ["localize_dict.json"],
        "key_exact": ["SingleMode585006"],
        "match_mode": "exact",
        "note": "Exact Career-mode Goal Race label. Keep the established player-facing term without matching generic objective/race prose.",
    },
    {
        "id": "career.ui.turn",
        "category": "career_ui",
        "ja": ["ターン"],
        "zh_cn": ["回合"],
        "target_vi": "Lượt",
        "source_paths": ["localize_dict.json"],
        "key_exact": ["SingleMode0537"],
        "match_mode": "exact",
        "note": "Exact Career turn-counter label. Vietnamese Lượt is compact and natural; generic 回合 prose remains outside the rule.",
    },
    {
        "id": "career.ui.rating",
        "category": "career_ui",
        "ja": ["評価"],
        "zh_cn": ["评价"],
        "target_vi": "Rating",
        "source_paths": ["localize_dict.json"],
        "key_exact": ["SingleModeScenarioBreeders508058"],
        "match_mode": "exact",
        "note": "Exact player-facing Rating label. common.rating intentionally has no global source alias, so this rule stays key-scoped.",
    },
    {
        "id": "career.ui.team_rating",
        "category": "career_ui",
        "ja": ["チーム評価"],
        "zh_cn": ["队伍评价"],
        "target_vi": "Team Rating",
        "source_paths": ["localize_dict.json"],
        "key_exact": ["SingleModeScenarioBreeders508040"],
        "match_mode": "exact",
        "note": "Exact scenario Team Rating label; do not promote bare 评价 to a global alias.",
    },
    {
        "id": "career.ui.scenario",
        "category": "career_ui",
        "ja": ["シナリオ"],
        "zh_cn": ["剧本"],
        "target_vi": "Scenario",
        "source_paths": ["localize_dict.json"],
        "key_exact": ["SingleModeScenarioTeamRace0033", "SingleModeScenarioTeamRace0037"],
        "match_mode": "contains",
        "note": "Player-facing Scenario wording is proven at these Career UI keys only. Bare 剧本 remains unsafe as a global alias because story/script prose is semantically overloaded.",
    },
    {
        "id": "race.ui.track.room_match",
        "category": "race_ui",
        "ja": ["コース"],
        "zh_cn": ["赛道"],
        "target_vi": "Track",
        "source_paths": ["localize_dict.json"],
        "key_exact": ["RoomMatch600128"],
        "match_mode": "contains",
        "note": "Exact Room Match course-setting UI uses the player-facing Track concept. Generic road/course prose and proper racecourse identities remain outside this rule.",
    },
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _upsert(terms: list[dict[str, Any]], record: dict[str, Any]) -> None:
    normalized = dict(record)
    normalized["locked"] = True
    normalized["match_mode"] = str(record.get("match_mode", "exact"))
    normalized["invalidation_scope"] = "item"
    for term in terms:
        if isinstance(term, dict) and term.get("id") == normalized["id"]:
            term.update(normalized)
            return
    terms.append(normalized)


def _exclude_trainee_from_world_term(repo_root: Path) -> None:
    path = repo_root / "glossary" / "ui_community_terms.json"
    if not path.exists():
        return
    payload = _load(path)
    terms = payload.setdefault("terms", [])
    world = next(
        (term for term in terms if isinstance(term, dict) and term.get("id") == "common.world.umamusume"),
        None,
    )
    if world is None:
        return
    exclusions = [str(value) for value in world.get("exclude_source_contains", []) if str(value)]
    for value in TRAINEE_SOURCE_FORMS:
        if value not in exclusions:
            exclusions.append(value)
    world["exclude_source_contains"] = exclusions
    _write(path, payload)


def _python_string_literal(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace("\n", "\\n").replace('"', '\\"')
    return f'"{escaped}"'


def _patch_player_facing_sync_source(repo_root: Path) -> None:
    path = repo_root / "scripts" / "enforce_player_facing_canon.py"
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    if all(_python_string_literal(value) in text for value in TRAINEE_SOURCE_FORMS):
        return
    anchor = '    "赛马娘Pretty Derby",\n]'
    replacement = (
        '    "赛马娘Pretty Derby",\n'
        '    "育成赛马娘",\n'
        '    "育成\\n赛马娘",\n'
        ']'
    )
    if anchor not in text:
        raise RuntimeError("Could not locate BRAND_EXCLUSIONS anchor in enforce_player_facing_canon.py")
    path.write_text(text.replace(anchor, replacement, 1), encoding="utf-8", newline="\n")


def harden(repo_root: Path = REPO_ROOT) -> None:
    path = repo_root / "glossary" / "term_registry.json"
    payload = _load(path)
    terms = payload.setdefault("terms", [])
    for record in SCOPED_UI_TERMS:
        _upsert(terms, record)
    _write(path, payload)
    _exclude_trainee_from_world_term(repo_root)
    _patch_player_facing_sync_source(repo_root)


if __name__ == "__main__":
    harden()

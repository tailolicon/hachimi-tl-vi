from __future__ import annotations

# text_data categories confirmed by the pinned JP-server corpus/tooling.
CATEGORY_KINDS = {
    "4": "trainee_card_full_name",
    "13": "gacha_banner_text",
    "16": "song_name",
    "17": "song_credit",
    "5": "trainee_card_title",
    "6": "character_name",
    "32": "race_name",
    "33": "race_display_name",
    "47": "skill_name",
    "75": "support_card_full_name",
    "76": "support_card_title",
    "77": "support_character_name",
    "78": "support_display_name",
    "128": "song_description",
    "131": "mission_objective",
    "150": "support_unique_effect_name",
    "170": "character_display_name",
    "171": "character_system_trigger",
    "172": "inheritance_description",
    "182": "character_name_alias",
}


def asset_kind_for_path(rel: str) -> str:
    path = "/" + rel.replace("\\", "/").lower().lstrip("/")
    if "/lyrics/" in path:
        return "lyrics"
    if "/race/storyrace/" in path or "/storyrace/" in path:
        return "race_story"
    if "/home/" in path:
        return "home"
    if "/story/" in path:
        return "story"
    return "asset"

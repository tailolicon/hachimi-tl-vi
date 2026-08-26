# Uma Musume translation context

This file is mandatory context for every translation worker. The repository, not chat memory, is the source of truth.

## Project scope

- Target game: **Uma Musume Pretty Derby, JP-server content** rendered through Hachimi Edge.
- Current translation source may be Japanese or a recent Simplified-Chinese community translation of the JP server. The pinned source snapshot in `work/translation_progress.json` is authoritative for each batch.
- Target language: natural Vietnamese for players, not a word-for-word gloss.
- Do not use UmaTL English translation text as AI input.

## World and lore model

Uma Musume are humanlike athletes inspired by real racehorses. They study/train at Tracen Academy, work with Trainers, compete in races, and may perform Winning Lives. Do not casually rewrite the setting as ordinary horse racing or call characters literal horses. Preserve the distinction between a character, the historical horse inspiration, a race/event name, and a gameplay system.

## Source-language rule

When the source is zh-CN, treat it as a **semantic bridge**, not the canonical spelling authority for proper nouns. Chinese-translated horse/character names must not be translated literally into Vietnamese. Resolve names through `glossary/term_registry.json` / `glossary/characters.json`; if no mapping exists, use an established canonical Roman-letter name only when confident. Otherwise preserve the proper noun rather than inventing a Vietnamese calque.

## Translation layers

1. **UI/system** — compact, immediately understandable, stable terminology. Fixed-size UI must also follow `UI_TRANSLATION_RULES.md`, `glossary/ui_short_forms.json`, and reviewed overrides in `glossary/ui_overrides.json`; visual fit is part of correctness.
2. **Training/career (育成)** — distinguish stats, energy, motivation, training, support-card mechanics, scenario mechanics, conditions and objectives.
3. **Skills/effects** — mechanical meaning has priority; preserve trigger conditions, distance/style restrictions, numbers and runtime tokens exactly.
4. **Race commentary** — concise, energetic Vietnamese sports commentary; never alter race state.
5. **Character/home/story/event** — preserve speaker personality, relationship, emotional subtext and continuity across adjacent lines.
6. **Lyrics** — preserve meaning and voice; natural rhythm is desirable but never at the expense of a materially different meaning.

## Core gameplay distinctions

- `スタミナ / 耐力` is the **Stamina stat** → `Thể lực`.
- `体力` is the expendable training **energy gauge** → `Năng lượng`; never collapse it into the Stamina stat.
- Running-style labels are canonical gameplay labels. This project uses `Nige`, `Senko`, `Sashi`, `Oikomi`, and `Dai Nige` instead of inventing several Vietnamese variants.
- `芝` is turf → `Sân cỏ`; `ダート` is dirt → `Dirt`.
- Distance categories are `Cự ly ngắn`, `Mile`, `Cự ly trung bình`, `Cự ly dài`.

## Names and entities

- Character/racehorse-inspired names are proper nouns. Prefer established Roman-letter game/community names.
- Do not translate a Chinese character name by its dictionary meaning.
- Race names, scenario names, facilities, skill names and item names may have conventional spellings; consult the registry before creating a new rendering.
- If an entity is ambiguous, do not silently create a permanent translation. Preserve the safest identifiable form and let later terminology review normalize it.

## Vietnamese dialogue and pronouns

Vietnamese pronouns encode relationship information that Japanese/Chinese may omit. Do not apply one global `tôi/bạn` mapping.

Use, in order:
1. explicit character profile rules in `glossary/characters.json`,
2. speaker/addressee/relationship context supplied with the entry,
3. surrounding lines and scene tone,
4. a neutral natural construction when the relationship is genuinely unknown.

Do not infer intimacy, seniority or hostility without evidence. Maintain the same relationship register across a scene unless the source intentionally changes it.

## Structural invariants

Preserve exactly when present:

- placeholders such as `{0}`, `{name}`, `%s`, `%d`, indexed printf tokens,
- rich-text/markup tags and color tags,
- `$VARIABLE`, `$(...)` and other runtime tokens,
- URLs, IDs and machine-readable identifiers,
- required newline structure unless an explicitly reviewed exception exists.

Never add translator notes to game text.

For fixed-size UI, do not insert extra newlines to rescue a long translation. Keep the source newline count and shorten the label instead. A reviewed entry in `glossary/ui_overrides.json` is authoritative over generated worker wording for that UI key.

## Worker behavior

Before translating any batch, read:

1. `PARALLEL_WORKERS.md`
2. `work/translation_progress.json`
3. `GAME_CONTEXT.md`
4. `glossary/term_registry.json`
5. `glossary/characters.json`
6. `glossary/style_rules.json`
7. `UI_TRANSLATION_RULES.md`
8. `glossary/ui_short_forms.json`

Do not rely on a worker's private chat history or on memory of the game when repository context conflicts with it. External research is a fallback for an unresolved entity, not a substitute for the shared registry.

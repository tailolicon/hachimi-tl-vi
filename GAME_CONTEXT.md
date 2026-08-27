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

When the source is zh-CN, treat it as a **semantic bridge**, not the canonical spelling authority for proper nouns or gameplay terminology. Chinese-translated horse/character names must not be translated literally into Vietnamese. Resolve names through `glossary/term_registry.json` / `glossary/characters.json`; if no mapping exists, use an established canonical Roman-letter name only when confident. Otherwise preserve the proper noun rather than inventing a Vietnamese calque.

Chinese gameplay labels are also not permission to create Vietnamese semantic calques for terms that players conventionally keep in English/Romanized form. For those concepts, `glossary/ui_community_terms.json` is the player-facing terminology layer.

**Individual skill names are the deliberate exception in style handling:** when a zh-CN skill title is available, use its compact title structure as the primary naming-style reference, while using the Japanese title/registry as the semantic guard for motifs, proper nouns, puns and distinctions. The exact rules and reviewed examples live in `glossary/skill_name_style.json`.

## Terminology precedence

Use this precedence when sources disagree:

1. a matching accepted form in `glossary/ui_community_terms.json` for player-facing common gameplay/UI terms or named mechanics/events;
2. for an **individual skill name**, an exact canonical example in `glossary/skill_name_style.json` intentionally overrides an older conflicting skill-name target;
3. a locked entry in `glossary/term_registry.json` for concepts not overridden by layers 1-2;
4. accepted observed terminology that does not conflict with 1-3;
5. official/player-established naming when the shared registries do not yet cover the concept;
6. generic Vietnamese translation only for genuinely generic text.

`ui_community_terms.json` intentionally overrides several older Vietnamese mappings in `term_registry.json` while the canonical registry is migrated. `skill_name_style.json` similarly carries a small set of reviewed skill-title overrides where the old canonical wording does not match the approved naming style. Do not use an old target as evidence that the old style is preferred when one of these higher-precedence layers explicitly supersedes it.

## Translation layers

1. **UI/system** — compact, immediately understandable, stable player-facing terminology. Fixed-size UI must also follow `UI_TRANSLATION_RULES.md`, `glossary/ui_short_forms.json`, `glossary/ui_community_terms.json`, and reviewed overrides in `glossary/ui_overrides.json`; visual fit is part of correctness.
2. **Training/career (育成)** — distinguish stats, energy, motivation, training, support-card mechanics, Scenario mechanics, Condition and objectives.
3. **Skills/effects** — distinguish the generic gameplay category (`Skill`, `Unique Skill`, `Evolution Skill`) from the **individual skill name**. Individual names follow `glossary/skill_name_style.json`; mechanical meaning has priority in descriptions, with trigger conditions, Distance/Style restrictions, numbers and runtime tokens preserved exactly.
4. **Race commentary** — concise, energetic Vietnamese sports commentary; never alter race state.
5. **Character/home/story/event** — preserve speaker personality, relationship, emotional subtext and continuity across adjacent lines.
6. **Lyrics** — preserve meaning and voice; natural rhythm is desirable but never at the expense of a materially different meaning.

## Common EN player-facing gameplay terms

For the concepts covered by `glossary/ui_community_terms.json`, keep the EN-version/player-facing term instead of translating it into Vietnamese. This includes the current reference set such as:

- `Trainer`
- `Speed`, `Stamina`, `Power`, `Guts`, `Wit`
- `Aptitude`, `Rating`, `Condition`
- `Legacy`, `Guest Legacy`, `Inspiration`, `Spark`
- `Scenario`, `Track`
- `Turf`, `Dirt`
- `Distance`, `Sprint`, `Mile`, `Medium`, `Long`
- `Style`
- `Front Runner` / compact `Front`
- `Pace Chaser` / compact `Pace`
- `Late Surger` / compact `Late`
- `End Closer` / compact `End`
- `Skill`, `Unique Skill`, `Evolution Skill`

Do not translate these into forms such as `Tốc độ`, `Thể lực`, `Sức mạnh`, `Ý chí`, `Trí tuệ`, `Sân cỏ`, `Cự ly ngắn`, `Lối chạy`, `Nige`, `Senko`, `Sashi`, or `Oikomi` when the matched concept is the player-facing gameplay label.

The training energy gauge remains a separate mechanic from the `Stamina` stat. Do not collapse them because both may be expressed by words related to stamina/energy in source languages.

## Individual skill-name localization

The keep-English rule above applies to common gameplay terminology and Skill **category labels**, not to the proper name of each skill.

For an individual skill name:

- follow `glossary/skill_name_style.json`;
- when zh-CN is available, learn from its **short title rhythm** instead of expanding it into explanatory Vietnamese;
- use JP/registry evidence to preserve proper nouns, puns, title/role imagery and distinctions the Chinese rendering may flatten;
- usually aim for roughly **2–4 meaningful title units** when the source itself is compact; this is a style target, not a hard word-count rule;
- prefer a natural Hán-Việt rendering when it is evocative, intelligible, and faithful;
- if a Hán-Việt rendering is stiff or opaque, choose a short, polished Vietnamese localization with the same kind of punch as commercial game/LoL skill naming;
- preserve a distinctive gimmick rather than normalizing it away: e.g. `弧线教授 / 弧線のプロフェッサー` is **Giáo Sư Cung Tuyến**, retaining the Professor image;
- compact mechanical families should also look like ability names rather than prose, e.g. `弯道加速○ → Gia Tốc Khúc Cua○`;
- preserve `○`, `×`, `◎`, `☆`, placeholders, markup and runtime symbols exactly;
- avoid literal machine-like noun piles and avoid turning a skill name into a sentence explaining its effect;
- preserve proper nouns, references, puns, or indispensable foreign wording when translating them would destroy the reference;
- keep mechanical details in the skill description exact even when the skill title is localized creatively.

Reviewed exact examples currently include `弧线教授 → Giáo Sư Cung Tuyến`, the graded `弯道加速/回复/巧者` families, and `强攻策 → Cường Công Kế`. Illustrative examples in the style file are guidance only until their JP identity/nuance is verified.

The goal is a name that sounds like a real ability name in a professionally localized game, not a dictionary gloss.

## Names and entities

- Character/racehorse-inspired names are proper nouns. Prefer established Roman-letter game/community names.
- Do not translate a Chinese character name by its dictionary meaning.
- Race names, Scenario names, facilities, skill names and item names may have conventional spellings; consult the registries before creating a new rendering.
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

For fixed-size UI, do not insert extra newlines to rescue a long translation. Keep the source newline count and shorten the label instead. A reviewed entry in `glossary/ui_overrides.json` is authoritative over generated worker wording unless superseded by the current UI-review policy.

## Worker behavior

Before translating any batch, read:

1. `PARALLEL_WORKERS.md`
2. `work/translation_progress.json`
3. `GAME_CONTEXT.md`
4. `glossary/ui_community_terms.json`
5. `glossary/skill_name_style.json`
6. `glossary/term_registry.json`
7. `glossary/characters.json`
8. `glossary/style_rules.json`
9. `UI_TRANSLATION_RULES.md`
10. `glossary/ui_short_forms.json`

Do not rely on a worker's private chat history or on memory of the game when repository context conflicts with it. External research is a fallback for an unresolved entity, not a substitute for the shared registry.

# Translation context maintenance

The context registry is shared infrastructure for every translation worker. Chat history and individual model memory are not authoritative.

## Files

- `GAME_CONTEXT.md` — compact world/game/translation bible for human and agent workers.
- `glossary/game_context.json` — machine-injected compact game context.
- `glossary/term_registry.json` — reviewed/locked JP ↔ zh-CN ↔ VI terminology.
- `glossary/characters.json` — generated canonical character identity registry plus preserved manual speech/relationship rules.
- `glossary/generated_candidates.json` — discovery queue for names of races, skills, support cards, scenarios and other entities. **Not canonical** until reviewed.
- `glossary/style_rules.json` — translation style by content type.

## Character registry

Run:

```bash
python scripts/sync_context_registry.py
```

The script reads `work/translation_progress.json`, fetches a structured character identity list, and joins it to the pinned zh-CN source's `text_data` category 6 by numeric game ID.

Generated records contain only compact identity fields needed by translation:

- game ID,
- canonical Latin name,
- Japanese name,
- zh-CN alias,
- internal/preferred identifier when available,
- official character link when available.

Long third-party profile prose is intentionally not copied into the registry. This reduces copyright/provenance risk and keeps prompts small.

### Manual fields survive regeneration

The sync script preserves manually reviewed fields when it can identify the same character:

- `speech_rules`
- `speech_traits`
- `relationships`
- `pronouns`
- `vi_notes`
- extra aliases

Do not put generated data and hand-authored notes in separate conflicting records. Use the game ID record after the first sync.

### Unresolved source identities

Any character/NPC name present in the pinned source category 6 but not resolvable from the structured roster is written to `unresolved_source_characters`. Workers must not invent a Vietnamese semantic translation for these names. A reviewer can map them later.

## Terminology discovery

Run:

```bash
python scripts/extract_context_candidates.py
```

The extractor currently recognizes Hachimi/master `text_data` categories including:

- character names,
- trainee/card names and titles,
- race names/display names,
- skill names,
- support-card names/titles/character names,
- support unique-effect names,
- scenario names conservatively detected from scenario-marked strings.

The output is `glossary/generated_candidates.json`. It is a review queue, not a translation dictionary. Batch workers must never treat an unreviewed candidate as a locked Vietnamese term.

Reviewed candidates should be promoted into `glossary/term_registry.json` with stable IDs, source aliases, `target_vi`, and an explicit `locked` decision.

## Prompt scaling

`src/hachimi_tl_vi/context_registry.py` prevents registry size from exploding prompt tokens.

For each translation batch the prompt receives:

1. a small fixed set of core gameplay terms,
2. terminology whose JP/zh-CN aliases actually appear in the batch text/context,
3. character records whose aliases actually appear in the batch text/context,
4. compact global game/style rules.

The complete 100+ character database and thousands of discovered skill/race candidates are therefore not copied into every request.

## Source pinning

Character zh-CN aliases and terminology candidates are always extracted from the exact upstream commit recorded in `work/translation_progress.json`.

When a new source snapshot is intentionally adopted, the normal source-sync workflow advances the pinned commit; the context sync can then regenerate against that snapshot. Context generation must never silently follow a moving source branch while translation batches remain pinned to an older commit.

## Automation

`.github/workflows/sync-context.yml` runs the context generators and tests. If generated registry files change, it commits them back to `main` after rebasing on the latest worker commits. It never force-pushes.

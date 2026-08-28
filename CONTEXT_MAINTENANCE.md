# Translation context maintenance

The context registry is shared infrastructure for every translation worker. Chat history and individual model memory are not authoritative.

## Files

- `GAME_CONTEXT.md` — compact world/game/translation bible for human and agent workers.
- `glossary/game_context.json` — machine-injected compact game context.
- `glossary/term_registry.json` — reviewed/locked JP ↔ zh-CN ↔ VI terminology.
- `glossary/observed_terms.json` — exact terminology memory learned from already merged entity translations; useful for consistency, but not canonical by itself.
- `glossary/generated_candidates.json` — discovery inventory for race/skill/support/scenario/name entities. **Not canonical** until reviewed.
- `glossary/terminology_review_queue.json` — ranked review work built from candidates + observed memory + canonical registry.
- `glossary/terminology_reviews.json` — explicit `lock` / `defer` / `ignore` decision ledger.
- `glossary/canonical_findings.json` — deduplicated systemic findings from retrospective review workers; blocking evidence, not canonical by itself.
- `glossary/characters.json` — generated canonical character identity registry.
- `glossary/speech_bible.json` — curated compact dialogue-style guidance; this is the only speech profile data injected into prompts.
- `glossary/speech_samples.json` — bounded dialogue evidence/statistics extracted from the pinned source; never treated as automatic personality claims.
- `glossary/speech_review_queue.json` — ranked character/NPC speech-profile work.
- `glossary/style_rules.json` — translation style by content type.

## Character registry

Run:

```bash
python scripts/sync_context_registry.py
```

The script reads `work/translation_progress.json`, fetches a structured character identity list, and joins it to the pinned zh-CN source's `text_data` category 6 by numeric game ID.

Generated records contain only compact identity fields needed by translation:

- game ID when reliably known,
- canonical Latin name,
- Japanese name,
- zh-CN alias,
- internal/preferred identifier when available,
- official character link when available.

Long third-party profile prose is intentionally not copied into the registry. Missing IDs are never inferred from row order; unresolved structured identities use a stable slug key until an ID is verified.

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

## Character Speech Bible

`glossary/speech_bible.json` stores compact reviewed translation guidance such as:

- register and formality,
- tempo/rhythm,
- meaningful self-reference rules,
- when slang or theatrical language is appropriate,
- explicit anti-rules such as “do not invent a dialect” or “do not force one pronoun pair”.

The profile is not a biography and must not replace source-scene evidence. Source wording and relationship context always have higher priority.

### Dialogue evidence sampler

Run against the exact pinned source checkout:

```bash
python scripts/extract_speaker_samples.py \
  --upstream-root PATH_TO_PINNED_SOURCE \
  --source-commit PINNED_SHA
python scripts/build_speech_review_queue.py
```

The sampler recursively scans dialogue blocks, resolves speaker aliases through `characters.json`, and keeps a deterministic bounded set of short evidence lines per character. It also records neutral signals such as average line length and punctuation rates.

These statistics are **evidence only**. They must not be used to infer fixed pronouns, hierarchy, dialect, intimacy, or personality without actual dialogue/profile review.

`.github/workflows/sync-speech-context.yml` checks out the exact `source_commit` from `work/translation_progress.json`, regenerates `speech_samples.json` + `speech_review_queue.json`, tests the pipeline, then safely rebases/pushes only those generated files.

## Terminology discovery and memory

Discover candidate entity names:

```bash
python scripts/extract_context_candidates.py
```

Build consistency memory from already merged `localized_data/text_data_dict.json`:

```bash
python scripts/build_observed_term_memory.py
```

The observed-memory builder only accepts a source entity when all merged occurrences agree on one Vietnamese target. If the same source has different merged targets, it is written to `conflicts` and excluded from prompt memory.

The candidate extractor recognizes Hachimi/master `text_data` categories including:

- character names,
- trainee/card names and titles,
- race names/display names,
- skill names,
- support-card names/titles/character names,
- support unique-effect names,
- scenario names conservatively detected from scenario-marked strings.

Generate the ranked review queue:

```bash
python scripts/build_terminology_review_queue.py
```

The queue ranks:

1. explicit locks that have not yet reached the registry,
2. conflicting merged translations,
3. unresolved character-like identities,
4. observed unique mappings that are good promotion candidates,
5. new untranslated skill/race/scenario/support entities.

Known character names are handled by `characters.json` and are not semantic-calqued.

## Explicit terminology decisions

`glossary/terminology_reviews.json` is the review ledger. Queue entries are never auto-promoted merely because they rank highly.

Supported actions:

- `lock` — explicitly promote a reviewed source → Vietnamese mapping;
- `defer` — mark reviewed but unresolved; no registry write;
- `ignore` — mark as not canonical terminology; no registry write.

Validate decisions without writing:

```bash
python scripts/apply_terminology_reviews.py --check
```

Apply explicit locks:

```bash
python scripts/apply_terminology_reviews.py
```

Safety properties:

- a lock requires explicit source + target;
- stable IDs are generated when no `term_id` is supplied;
- an existing locked alias may not be remapped to a different Vietnamese target;
- an existing term ID may not silently change meaning;
- aliases spanning different existing canonical concepts fail validation;
- reapplying an already matching decision is idempotent.

After application, rebuild `terminology_review_queue.json`. `defer`/`ignore` decisions leave the actionable queue; a `lock` remains high priority until `term_registry.json` actually contains it.

## Canonical findings from retrospective audit

Review workers report reusable systemic defects through their own result instead of editing canonical files. The merge pipeline deduplicates them into `glossary/canonical_findings.json`. Open findings are excluded from the global 19k context hash and participate only in item-scoped invalidation. Matching decisions are deferred until the finding is resolved; unrelated reviewed entries remain reusable. Evidence growth for the same finding does not change review identity.

`build_terminology_review_queue.py` ranks open findings ahead of ordinary conflicts/candidates. A maintainer verifies and lands the canonical/context rule, explicitly ignores the finding, or defers it. Matching canonical targets deterministically resolve findings on refresh; defer remains blocking. The intended loop is `audit discovery → blocking finding → canonical verification/lock → affected entries reopen → audit continues`.


## Prompt scaling and precedence

`src/hachimi_tl_vi/context_registry.py` prevents registry size from exploding prompt tokens.

For each translation batch the prompt receives only:

1. a small fixed set of core gameplay terms,
2. canonical terminology whose JP/zh-CN aliases appear in the batch,
3. exact unique observed terminology relevant to the batch,
4. character records whose aliases appear in text/context,
5. speech profiles for those selected characters,
6. compact global game/style rules.

Precedence is:

`source scene/context > locked canonical registry > unique observed memory > general style guidance`

Character identity mapping is canonical for names; unreviewed discovered candidates are never injected as locked translations.

## Source pinning

Character aliases, terminology candidates and speech evidence are always extracted from the exact upstream commit recorded in `work/translation_progress.json`.

When a new source snapshot is intentionally adopted, the source-sync workflow advances the pinned commit; context/speech sync can then regenerate against that snapshot. Context generation must never silently follow a moving source branch while translation batches remain pinned to an older commit.

## Automation

- `.github/workflows/sync-context.yml` regenerates identity/candidate data, applies only explicit terminology review decisions, rebuilds terminology review state, runs tests and commits only whitelisted context files.
- `.github/workflows/sync-speech-context.yml` regenerates pinned dialogue evidence and the speech review queue.
- `.github/workflows/merge-results.yml` refreshes observed terminology and the terminology review queue after merged translation batches.

All three workflows use safe fast-forward/rebase behavior around active translation-worker commits; none force-pushes or owns worker claim/result/canonical-progress files.

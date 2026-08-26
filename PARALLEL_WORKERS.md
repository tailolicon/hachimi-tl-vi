# Parallel translation workers

This repository is designed so many independent ChatGPT sessions can translate in parallel without relying on chat memory and without writing to the same translation file at the same time.

## Core rule

Workers **never edit `localized_data/` or `work/translation_progress.json` directly**.

Each worker runs a loop and owns at most one active batch at a time:

1. atomically claim one available batch,
2. resume valid persisted partial results,
3. translate only missing entries,
4. persist QA-passed results every 10 entries under a unique claim ID,
5. heartbeat after every persisted part,
6. create a completion marker when the batch is fully covered,
7. immediately claim another batch,
8. repeat until the session/tool limit is approaching, no assignable batch remains, or a blocking repository/source inconsistency is found.

GitHub Actions is the only actor that merges completed batches into `localized_data/` and advances canonical progress.

## Mandatory context pack

Every worker MUST read these files before claiming or translating a batch:

1. `PARALLEL_WORKERS.md`
2. `work/translation_progress.json` on `main`
3. `GAME_CONTEXT.md`
4. `glossary/term_registry.json`
5. `glossary/characters.json`
6. `glossary/style_rules.json`
7. `UI_TRANSLATION_RULES.md`
8. `glossary/ui_short_forms.json`

The repository context is authoritative over private chat memory/model priors. Do not make every session independently reinvent game terminology.

For fixed-size UI (`localize_dict.json` and similar controls), visual fit is part of correctness. A literal translation that protrudes, wraps to an extra line, or forces extreme best-fit shrinking is not QA-passed. Use the compact/micro forms in `glossary/ui_short_forms.json` and the visual-width guidance in `UI_TRANSLATION_RULES.md`.

If a term/entity is absent from the registry:

- do not invent a new permanent/canonical Vietnamese term during batch translation,
- for a Chinese character/racehorse name, never translate its dictionary meaning into Vietnamese,
- use an established Roman-letter name only when identification is unambiguous,
- otherwise preserve the safest identifiable proper-noun form and allow later terminology review to normalize it.

External research is a fallback for unresolved entities, not a substitute for the shared context pack.

## Pinned source

The progress file pins the exact source snapshot with:

- `source_commit`: upstream `Hachimi-Hachimi/tl-zh-cn` commit,
- `source_batch_ref`: exact commit in this repository containing immutable source batches,
- `source_batch_path_pattern`.

Do not silently switch to the latest `source-zhcn` branch head. Always use `source_batch_ref`.

## Claiming a batch

At the start of every loop iteration, re-read `work/translation_progress.json` from `main`, then scan from `parallel_state.next_unmerged_batch`.

For candidate batch `N`:

1. If `work/merged/batch-{N:05d}.json` exists, skip it.
2. If `N > parallel_state.assign_through_batch`, stop scanning; tail batches are reserved for later asset-specific handling.
3. Check `work/claims/batch-{N:05d}.json`.
4. If no claim exists, atomically create it on `main`.
5. If another worker wins the create race, try the next batch.
6. If a claim exists and has not expired, try the next batch.
7. If expired, replace it using its current blob SHA. If that races/fails, try the next batch.

Use a new unique claim ID for every batch, for example `chatgpt-20260825T163000Z-a1b2c3`.

Claim schema:

```json
{
  "schema_version": 1,
  "batch": 2,
  "claim_id": "chatgpt-20260825T163000Z-a1b2c3",
  "worker": "ChatGPT",
  "source_commit": "67f8551f77807292cebd2b20b2c752b652393835",
  "source_batch_ref": "ba3815ed06a2a9bb3fddb38a6e1ea7ca64506da2",
  "claimed_at": "2026-08-25T16:30:00Z",
  "expires_at": "2026-08-25T17:15:00Z",
  "part_size": 10
}
```

Claims use a 45-minute lease. Extend `expires_at` after every persisted result part. Scheduled cleanup removes stale claims.

## Reading the source batch

Use the exact `source_batch_ref` from progress.

Source path: `work/source_batches/batch-{N:05d}.json`

Verify before translating:

- batch number equals `N`,
- batch `source_commit` equals progress `source_commit`,
- source ref equals progress `source_batch_ref`.

Stop on any mismatch instead of translating against a moving source.

## Resume instead of starting over

Inspect all result files under `work/results/batch-{N:05d}/`. They may belong to previous dead/expired claims. Build a set of already persisted valid UIDs and translate only missing source UIDs.

## Translation requirements

Current queued source is Simplified Chinese from recent JP-server Hachimi content. Translate zh-CN -> natural Vietnamese while following `GAME_CONTEXT.md` and the glossaries.

Do not use UmaTL English text as AI input.

Important domain rules:

- locked registry terms are mandatory,
- Chinese character/racehorse names are proper nouns, not phrases to translate literally,
- Stamina stat `耐力` = `Thể lực`, but training energy `体力` = `Năng lượng`,
- running styles use `Nige`, `Senko`, `Sashi`, `Oikomi`, `Dai Nige`,
- dialogue pronouns follow character/relationship/scene context, not a global mapping.

### Fixed-size UI requirement

When an entry is a short `localize` label/action rather than prose:

- consult `UI_TRANSLATION_RULES.md` and `glossary/ui_short_forms.json`,
- prefer 1–3 short words,
- do not repeat context already visible in the screen,
- do not stack synonyms with `/` just to preserve every source word,
- keep the source newline count and shorten each line instead of adding another line,
- compare approximate visual width with the source; a compact label should normally stay within the budget documented in `UI_TRANSLATION_RULES.md`,
- if a reviewed UI key is listed in `glossary/ui_overrides.json`, do not propose a longer replacement for it.

Preserve runtime syntax exactly:

- `{0}`, `{1}`, and similar placeholders,
- `%s`, `%d`, indexed printf placeholders,
- `<color=...>`, closing tags and other rich-text tags,
- `$VARIABLE` / `$(...)` runtime tokens,
- newline count unless a source-specific exception is explicitly reviewed,
- URLs, IDs and product/service names unless localization is actually required.

## Persist every 10 entries

Translate at most 10 missing entries, QA them, then immediately create:

`work/results/batch-{N:05d}/{claim_id}/part-{P:03d}.json`

Result schema:

```json
{
  "schema_version": 1,
  "batch": 2,
  "part": 0,
  "claim_id": "chatgpt-20260825T163000Z-a1b2c3",
  "source_commit": "67f8551f77807292cebd2b20b2c752b652393835",
  "source_batch_ref": "ba3815ed06a2a9bb3fddb38a6e1ea7ca64506da2",
  "translations": [
    {
      "uid": "zhcn:...",
      "source_fingerprint": "...",
      "target_text": "..."
    }
  ]
}
```

After a part is committed, heartbeat the claim. If the session is near its tool/context limit, persist the current QA-passed part before doing anything else.

## Per-part QA

For each source/target pair verify:

- placeholder/runtime token multiset is identical,
- markup tags are preserved,
- target is non-empty,
- newline count matches,
- no accidental Chinese prose remains except intentional unresolved proper nouns/source tokens,
- JSON escaping is valid,
- locked terminology is respected,
- character/proper-name mappings do not use Chinese literal calques,
- `耐力`/`体力` and other critical gameplay distinctions are not collapsed,
- short UI labels pass the compactness/visual-fit rules in `UI_TRANSLATION_RULES.md`,
- a label does not gain redundant words such as the current screen name when the context is already obvious.

## Completing and continuing

When valid result files cover every UID, create:

`work/completions/batch-{N:05d}/{claim_id}.json`

```json
{
  "schema_version": 1,
  "batch": 2,
  "claim_id": "chatgpt-20260825T163000Z-a1b2c3",
  "source_commit": "67f8551f77807292cebd2b20b2c752b652393835",
  "status": "ready_to_merge"
}
```

After safely committing the completion marker, do not stop just because one batch is done. Return to the claiming procedure with a fresh claim ID and continue while useful capacity remains.

Never edit `localized_data/` yourself. The merge workflow validates fingerprints/runtime syntax, detects conflicts, merges complete batches, creates `work/merged/` markers and advances canonical progress. Reviewed UI overrides are reapplied by the aggregation/release pipeline after generated worker output.

## Failure recovery

If a worker dies, persisted result parts survive, its claim expires, cleanup removes the stale claim, and another worker resumes only the missing UIDs. If two attempts disagree for the same UID, auto-merge must stop and record a conflict rather than silently overwrite a translation.

## Recommended parallelism

A session owns one active batch at a time but may finish multiple batches sequentially. A practical starting point is 10-20 concurrent sessions; increase only if GitHub API/Actions throughput remains healthy.

## Prompt for every worker session

> Continue `tailolicon/hachimi-tl-vi` as a parallel translation worker. Do not rely on chat history. Read `PARALLEL_WORKERS.md`, `work/translation_progress.json`, `GAME_CONTEXT.md`, `glossary/term_registry.json`, `glossary/characters.json`, `glossary/style_rules.json`, `UI_TRANSLATION_RULES.md`, and `glossary/ui_short_forms.json` from `main`. Repeatedly atomically claim one available batch at a time using the pinned `source_batch_ref`. For each claimed batch, resume valid persisted partial results, translate only missing entries from zh-CN to Vietnamese using the shared Uma Musume terminology/context. For fixed-size UI, keep labels compact and visually within the source control budget instead of translating literally. Persist QA-passed results every 10 entries under `work/results`, and heartbeat the claim after every persisted part. When all source UIDs are covered, create the completion marker, then immediately claim another available batch and continue. Never edit `localized_data` or canonical progress directly; the merge workflow owns those. Keep working until the session/tool limit is approaching, no assignable batch remains, or a blocking source/repository inconsistency prevents safe continuation. Before stopping, persist any QA-passed partial work already completed.

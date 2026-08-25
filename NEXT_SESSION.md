# Next-session handoff

This file is the canonical handoff for continuing the Vietnamese Hachimi translation in a fresh ChatGPT session.

## Canonical state

Do **not** rely on chat memory. Always read these files from GitHub first:

1. `work/translation_progress.json` on branch `main`
2. `work/source_batches/manifest.json` on branch `source-zhcn`

The progress file is authoritative for `next_batch`. The manifest is authoritative for the current source queue and source commit.

## How to locate the next batch

1. Read `work/translation_progress.json` from `main`.
2. Let `N = next_batch`.
3. Fetch `work/source_batches/batch-{N:05d}.json` from branch `source-zhcn`.
4. Verify `source_commit` in the batch equals `source_commit` in the progress file. If they differ, stop and reconcile the source update before translating.

Example at the time this handoff was created:

- `next_batch = 2`
- batch path: `work/source_batches/batch-00002.json`
- source branch: `source-zhcn`
- source commit: `67f8551f77807292cebd2b20b2c752b652393835`

## Translation procedure

For every entry in the batch:

1. Translate `source_text` from Simplified Chinese (`zh-CN`) to natural Vietnamese (`vi`).
2. Keep game terminology consistent with the repository glossary and already translated strings.
3. Preserve all runtime syntax exactly:
   - placeholders such as `{0}`, `{1}`, `%s`, `%d`
   - rich-text/XML-like tags such as `<color=...>...</color>`
   - escaped control sequences
   - intended newline structure
   - numbers, IDs, URLs, product/service names unless they genuinely require localization
4. Do not translate keys, IDs, hashes, JSON paths, filenames, or locator metadata.
5. Do not use UmaTL English text as AI input. This queue comes from `Hachimi-Hachimi/tl-zh-cn`.

## Where translated text is written

For dictionary batches (`localize`, `text_data`, `character_system_text`, `race_jikkyo_comment`, `race_jikkyo_message`, `hashed`), write the Vietnamese value into the matching file under `localized_data/` on branch `main`, at the same logical key/path represented by the batch entry.

For asset-like entries, preserve the upstream JSON structure and replace only the translatable leaf represented by `json_path`; do not invent or flatten asset structure.

## QA required before marking a batch complete

A batch is complete only after all entries have been translated and checked for:

- identical placeholder multiset between source and target
- balanced/preserved rich-text tags
- no accidentally removed runtime tokens
- correct JSON encoding/escaping
- terminology consistency
- no untranslated Chinese prose unless intentionally retained as a proper noun or source-specific token

If any entry is unresolved, leave the batch as unfinished and do **not** advance `next_batch`.

## Commit/checkpoint order

Treat one batch as an atomic unit:

1. Write/commit the translated output on `main`.
2. Verify the written values and QA.
3. Only then update `work/translation_progress.json` on `main`:
   - append `N` to `translated_batches`
   - append `N` to `reviewed_batches`
   - append `N` to `qa_passed_batches`
   - add the actual number of translated entries to `translated_entries`
   - set `next_batch` to the next unfinished batch
4. Commit the checkpoint.

Never advance the checkpoint before the output is safely written.

## Queue scope

The optimized active queue contains UI/MDB and other high-priority non-story content. `story` and `home` are intentionally deferred to a separate context-aware/deduplicated phase. Do not accidentally pull the old full 14,486-batch queue back into the active workflow.

At the time of this file:

- active queued entries: 131,560
- active batches: 1,645 at 80 entries/batch
- deferred story/home entries: 1,027,265

When the upstream source changes, regenerate/reconcile the queue first and use fingerprints/source commits to determine what actually needs retranslating.

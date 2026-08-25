# Parallel translation workers

This repository is designed so many independent ChatGPT sessions can translate in parallel without relying on chat memory and without writing to the same translation file at the same time.

## Core rule

Workers **never edit `localized_data/` or `work/translation_progress.json` directly**.

Each worker runs a loop and owns at most one active batch at a time:

1. atomically claim one available batch,
2. resume valid persisted partial results for that batch,
3. translate only missing entries,
4. persist QA-passed results every 10 entries under a unique claim ID,
5. heartbeat the claim after every persisted part,
6. create a completion marker when the batch is fully covered,
7. immediately scan for and claim another available batch,
8. repeat until the session/tool limit is approaching, no assignable batch remains, or a blocking repository/source inconsistency is found.

Do **not** wait for the merge workflow before claiming the next batch. GitHub Actions is the only actor that merges completed batches into `localized_data/` and advances canonical progress.

This prevents cross-session file conflicts, makes partial work durable, and lets a healthy session complete multiple batches rather than stopping after one.

## Read these files first

Every new worker session must read:

- `PARALLEL_WORKERS.md`
- `work/translation_progress.json` on `main`

The progress file pins the exact source snapshot with:

- `source_commit`: upstream `Hachimi-Hachimi/tl-zh-cn` commit
- `source_batch_ref`: exact commit in this repository containing immutable source batches
- `source_batch_path_pattern`

Do not silently switch to the latest `source-zhcn` branch head. Always use `source_batch_ref`.

## Claiming a batch

At the start of every loop iteration, re-read `work/translation_progress.json` from `main`, then scan from `parallel_state.next_unmerged_batch`.

For each candidate batch `N`:

1. If `work/merged/batch-{N:05d}.json` exists, skip it.
2. If `N > parallel_state.assign_through_batch`, stop scanning. Tail batches are reserved for later asset-specific handling.
3. Check `work/claims/batch-{N:05d}.json`.
4. If no claim exists, atomically create it on `main`.
5. If another worker created it first, the create will fail; try the next batch.
6. If the claim exists and has not expired, try the next batch.
7. If the claim is expired, replace it using its current blob SHA. If that update races and fails, try the next batch.

Use a new unique claim ID for every batch claimed by the session, for example:

`chatgpt-20260825T163000Z-a1b2c3`

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

Claims use a 45-minute lease. Extend `expires_at` after every persisted result part. A scheduled workflow removes stale claims.

## Reading the source batch

Use the exact `source_batch_ref` from `work/translation_progress.json`.

Source path:

`work/source_batches/batch-{N:05d}.json`

Verify before translating:

- batch number is `N`
- batch `source_commit` equals progress `source_commit`
- source ref equals progress `source_batch_ref`

If any mismatch exists, stop instead of translating against a moving source.

## Resume instead of starting over

Before translating, inspect all existing result files under:

`work/results/batch-{N:05d}/`

They may belong to previous claim IDs from sessions that died. Build a set of already persisted valid UIDs and translate only source UIDs that are still missing.

A new worker may finish a batch started by an expired/dead worker.

## Persist every 10 entries

Do not hold an entire 80-entry batch only in chat context.

Translate at most 10 missing entries, QA them, then immediately create:

`work/results/batch-{N:05d}/{claim_id}/part-{P:03d}.json`

on `main`.

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

After the part is safely committed, heartbeat the claim by extending its expiry. If the session dies after that, the committed part remains usable. At most the current uncommitted 10-entry part is lost.

If the session/tool budget appears nearly exhausted, prioritize persisting the current QA-passed partial part and heartbeat rather than starting a new 10-entry chunk.

## Translation requirements

Translate Simplified Chinese to natural Vietnamese. Do not use UmaTL English text as AI input.

Preserve runtime syntax exactly:

- `{0}`, `{1}`, and similar placeholders
- `%s`, `%d`, indexed printf placeholders
- `<color=...>`, closing tags, and other rich-text tags
- `$VARIABLE` / `$(...)` runtime tokens
- newline count unless a source-specific exception is explicitly reviewed
- URLs, IDs, and product/service names unless localization is actually required

Keep terminology consistent with repository glossaries and previously merged Vietnamese strings.

## Per-part QA

Before persisting a part, verify each source/target pair:

- placeholder/runtime token multiset is identical
- markup tags are preserved
- target is non-empty
- newline count matches
- no accidental Chinese prose remains except intentional proper nouns/source tokens
- JSON escaping is valid
- terminology is consistent

## Completing a batch and continuing

When valid result files across all attempts cover every UID in the source batch, create:

`work/completions/batch-{N:05d}/{claim_id}.json`

Example:

```json
{
  "schema_version": 1,
  "batch": 2,
  "claim_id": "chatgpt-20260825T163000Z-a1b2c3",
  "source_commit": "67f8551f77807292cebd2b20b2c752b652393835",
  "status": "ready_to_merge"
}
```

After this marker is safely committed, **do not stop just because the batch is complete**. Return to the claiming procedure, use a fresh claim ID, and claim another available batch. Continue this loop while there is enough session/tool capacity to make useful progress.

Do not edit `localized_data/` yourself.

The `Merge parallel translation results` workflow will collect result parts, verify source/fingerprints/runtime syntax, refuse conflicts, merge fully covered batches into `localized_data/`, create `work/merged/` markers, update canonical progress, and trigger normal validation/release.

## Failure recovery

If a worker session dies:

- persisted result parts are not lost,
- its claim expires,
- the stale-claim workflow removes the claim,
- another session claims the same batch,
- the new session reads existing parts and translates only missing UIDs.

If two attempts produce different translations for the same UID, auto-merge stops for that batch and records the conflict in `work/merge_diagnostics.json`. A reviewer must resolve it; no translation is silently overwritten.

## Recommended parallelism

A session owns one active batch at a time, but may complete **multiple batches sequentially** during its lifetime.

Because claims are atomic, launch many sessions with the same prompt; they self-assign different available batches. A practical starting point is 10-20 concurrent sessions. Increase only if GitHub API/Actions throughput remains healthy.

## Prompt for every worker session

Use the same prompt in every new session:

> Continue `tailolicon/hachimi-tl-vi` as a parallel translation worker. Do not rely on chat history. Read `PARALLEL_WORKERS.md` and `work/translation_progress.json` from `main`. Repeatedly atomically claim one available batch at a time using the pinned `source_batch_ref`. For each claimed batch, resume valid persisted partial results, translate only missing entries from zh-CN to Vietnamese, persist QA-passed results every 10 entries under `work/results`, and heartbeat the claim after every persisted part. When all source UIDs are covered, create the completion marker, then immediately claim another available batch and continue. Never edit `localized_data` or canonical progress directly; the merge workflow owns those. Keep working until the session/tool limit is approaching, no assignable batch remains, or a blocking source/repository inconsistency prevents safe continuation. Before stopping, persist any QA-passed partial work already completed.

# Parallel translation worker protocol

This is the canonical protocol for running many ChatGPT translation sessions at the same time.

## Read these first

1. `work/parallel_state.json` on `main`.
2. The current epoch metadata referenced by `current_epoch_metadata`.
3. This file.

Do not use `work/translation_progress.json.next_batch` as a lock or global cursor. The old single-session cursor is deprecated.

## Retrospective review gate

Before choosing or claiming **any** new translation shard, inspect `work/parallel_state.json.translation_review_gate`.

If `translation_review_gate.enabled` is `true` or `claims_allowed` is `false`:

- DO NOT create a new translation claim;
- DO NOT take over an expired translation claim;
- DO NOT start translating an unclaimed shard;
- switch to `TRANSLATION_REVIEW.md` and claim retrospective review work instead.

The gate exists so all already merged Vietnamese translations can be re-reviewed against the completed speech and terminology context before translation resumes. Existing translation progress is preserved. The gate is cleared automatically only after every canonical entry has a resolved `keep` or `revise` decision; `defer` remains unresolved.

## Architecture

The source queue is immutable for an epoch. Workers never translate from the moving `source-zhcn` branch directly. They fetch source batches from the exact `source_queue_git_commit` pinned in the epoch metadata.

A source batch normally contains 80 entries. A parallel task is a 20-entry shard of that batch. A normal batch therefore has four tasks: `s00`, `s01`, `s02`, and `s03`.

Worker output is append-only/isolated by task:

- claims: `work/parallel/<epoch>/claims/<group>/<task-id>.json`
- partial/final results: `work/parallel/<epoch>/results/<group>/<task-id>.json`
- completion markers: `work/parallel/<epoch>/completed/<group>/<task-id>.json`
- aggregator markers: `work/parallel/<epoch>/aggregated/<group>/<task-id>.json`

`<group>` is `bNNNN`, where `NNNN = floor(batch / 100)` zero-padded to four digits. Example: batch 2 uses `b0000`; batch 237 uses `b0002`.

## Worker identity

At the start of a fresh session, create a unique worker id such as:

`sol-20260825T1630Z-a1b2`

Do not reuse another live worker id.

## Choosing work

Workers may choose tasks in any order only when the retrospective review gate is open. This is intentional so many sessions can spread out instead of all racing for the lowest batch.

1. Re-check `translation_review_gate`; stop here if it is enabled.
2. Use the current epoch's `first_parallel_batch` through `queue_total_batches`.
3. Pick a candidate batch and shard. A deterministic spread is recommended: hash the worker id and use it as a starting offset, then probe forward.
4. Fetch the pinned source batch from:
   `work/source_batches/batch-{batch:05d}.json`
   using the epoch's exact `source_queue_git_commit` as the Git ref.
5. Compute the shard slice:
   `start = shard * task_size`
   `end = min(start + task_size, len(batch.entries))`
   If `start >= len(batch.entries)`, the shard does not exist; choose another task.
6. Skip any batch listed in `legacy_completed_batches`.

## Atomic claim / lease

Before translating, re-check the retrospective review gate, then claim the task by creating its claim file on `main`.

A new claim must contain at least:

```json
{
  "schema_version": 1,
  "epoch": "zhcn-...",
  "task_id": "batch-00002-s00",
  "batch": 2,
  "shard": 0,
  "worker_id": "sol-...",
  "source_commit": "...",
  "source_queue_git_commit": "...",
  "claimed_at": "UTC ISO-8601",
  "heartbeat_at": "UTC ISO-8601",
  "lease_expires_at": "UTC ISO-8601",
  "status": "active"
}
```

Creating a claim file is the lock. If creation fails because another session created it first, do not overwrite it blindly; inspect it and choose another task.

If a claim already exists:

- if a completion marker exists, the task is done; skip it;
- if the claim is active and its lease has not expired, skip it;
- if the lease has expired, another worker may take over by updating the claim with a new worker id and lease, but only if the retrospective review gate is open. Use the current claim blob SHA so GitHub provides optimistic concurrency; if the update conflicts, another worker won the takeover and you must skip it.

Before taking over an expired task, fetch its result file. If it contains partial translations, resume from the first missing entry instead of retranslating saved work.

Default lease length is defined in epoch metadata. Refresh the lease after each saved checkpoint.

## Result file and crash-safe checkpoints

A worker NEVER writes directly to `localized_data/` while translating. It writes only its own task result file.

Result schema:

```json
{
  "schema_version": 1,
  "epoch": "zhcn-...",
  "task_id": "batch-00002-s00",
  "batch": 2,
  "shard": 0,
  "shard_start": 0,
  "shard_end_exclusive": 20,
  "source_commit": "...",
  "source_queue_git_commit": "...",
  "worker_id": "sol-...",
  "status": "partial",
  "translated_count": 5,
  "entries": [
    {
      "entry_index": 0,
      "uid": "...",
      "kind": "localize",
      "source_text": "...",
      "source_fingerprint": "...",
      "source_path": "localize_dict.json",
      "json_path": ["..."],
      "target_text": "...",
      "reviewed": true
    }
  ],
  "updated_at": "UTC ISO-8601"
}
```

Save the result file after every `checkpoint_every_entries` newly translated entries (currently 5). Save the result FIRST, then refresh the claim heartbeat/lease. This ordering ensures that if a session dies between writes, translated text is still preserved.

If a result file already exists, update it using its current blob SHA. Never replace already saved target text unless you are deliberately correcting it during review.

## Translation rules

Translate `source_text` from Simplified Chinese (`zh-CN`) into natural Vietnamese.

For every entry:

- preserve placeholders exactly (`{0}`, `{1}`, `%s`, `%d`, etc.);
- preserve rich-text/runtime tags exactly (`<color=...>`, `</color>`, etc.);
- preserve intended newline count/structure;
- preserve escaped runtime sequences;
- keep names, IDs, URLs and service/product names unchanged unless localization is genuinely required;
- keep terminology consistent with repository glossary and already reviewed Vietnamese strings;
- do not translate keys, hashes, JSON paths, filenames or locator metadata;
- do not use UmaTL English text as AI input.

Use at least these passes before completion:

1. semantic translation;
2. Vietnamese fluency/terminology review;
3. placeholder/markup/newline QA.

## Completing a task

A task is complete only when every source entry in its shard has one reviewed target entry and structural QA passes.

1. Save the result file with `status: "complete"` and the full shard translations.
2. Create the completion marker file. It must identify the result path, worker, epoch, source commits, entry count, completion timestamp, and set `qa_passed: true`.
3. Update the claim to `status: "complete"` if possible. If the session dies after step 2, the completion marker is authoritative and another worker will still skip the task.
4. Claim another task only if the retrospective review gate is still open and session time remains.

Do not mutate any shared global cursor after completion.

## Aggregation

Workers do not merge their own results into Hachimi output. `.github/workflows/aggregate-results.yml` periodically scans completion markers, independently validates each result against the pinned source batch, applies valid completed tasks to `localized_data/`, regenerates `index.json`, and publishes the `release` branch.

This separation is what makes many simultaneous workers safe. A worker crash cannot lose already checkpointed translations, and two workers cannot overwrite the same output file while translating.

## Source updates

`source-zhcn` may continue syncing every day. That must not change the source underneath an active epoch. Workers always use the epoch's pinned `source_queue_git_commit`.

A newer upstream snapshot should create/reconcile a new epoch and use source fingerprints to carry forward unchanged translations. Never silently repoint an existing epoch to a moving source branch.

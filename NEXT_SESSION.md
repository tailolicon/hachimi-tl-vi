# Next-session handoff

This project now uses parallel workers.

Do not rely on chat memory.

Read, in this order:

1. `PARALLEL_WORKERS.md`
2. `work/translation_progress.json`

Then act as one parallel worker:

- claim one available batch atomically,
- use the exact pinned `source_batch_ref`,
- resume persisted partial results if they exist,
- translate only missing entries,
- persist results every 10 entries,
- heartbeat the claim after each persisted part,
- create the completion marker only when all source UIDs are covered,
- never edit `localized_data/` or canonical progress directly.

GitHub Actions merges completed batches and updates canonical progress.

The old single-worker rule "always translate next_batch" is obsolete. `next_batch` is now only the lowest known unmerged batch and a starting point for scanning; different workers should claim different batches.

If the current upstream translation source changes, do not automatically move active workers to the new source. Existing workers must continue using the pinned `source_batch_ref` until a deliberate source reconciliation/promotion updates canonical progress.

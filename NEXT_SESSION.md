# Next-session handoff

This repository now uses the parallel leased-shard protocol.

Do **not** rely on chat memory and do **not** use the old `next_batch` single-session cursor.

## Required startup sequence

1. Read `PARALLEL_TRANSLATION.md` on `main`.
2. Read `work/parallel_state.json` on `main`.
3. Read the epoch file referenced by `current_epoch_metadata`.
4. Create a unique worker id for this session.
5. Select and atomically claim one available shard using the claim/lease protocol.
6. Fetch the source batch using the exact pinned `source_queue_git_commit`, never the moving `source-zhcn` branch.
7. Translate the shard and checkpoint the result after every configured checkpoint (currently 5 entries).
8. On completion, write the completed result and completion marker, then claim another shard if time remains.

Workers must not write directly to `localized_data/` and must not advance a global `next_batch`. The scheduled aggregator performs validated merging into Hachimi output.

## Current migration state

Batch 1 was translated before the parallel protocol and is recorded as a legacy-completed batch in the current epoch. Do not claim it.

All later work is claimed in small shards, so many fresh ChatGPT sessions can run concurrently without overwriting one another.

## Suggested user prompt for a fresh session

> Continue `tailolicon/hachimi-tl-vi` as a parallel translation worker. Read `PARALLEL_TRANSLATION.md`, `work/parallel_state.json`, and the current epoch metadata from GitHub. Generate a unique worker id, atomically claim an available task, translate it from the pinned source snapshot, save partial results at every configured checkpoint, perform terminology and structural QA, mark the task complete, and continue claiming more tasks while time remains. Never rely on chat memory, never use the moving source branch directly, and never overwrite another live worker's claim.

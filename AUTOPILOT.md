# Repository autopilot lifecycle

This file defines the persistent worker lifecycle from the current canonical-hardening phase through the remaining pinned corpus and final audits. `WORKER_START.md` is the only human entrypoint; this file is loaded by workers after the live router state.

Repository state is authoritative. Chat history is not.

## Global priority

1. blocking repository maintenance/canonical hardening;
2. unresolved systemic canonical findings that would otherwise propagate inconsistency;
3. retrospective translation review;
4. retrospective UI review;
5. normal translation of the current pinned queue;
6. expansion of deferred pinned-source content into the next translation wave;
7. post-completion full-corpus audits;
8. final release verification.

Quality gates always outrank raw translation percentage.

## Persistent files

- `WORKER_START.md` — universal entrypoint.
- `work/orchestration/state.json` — current phase, active maintenance task, roadmap and transitions.
- `work/orchestration/maintenance_claim.json` — single-writer lease for serial maintenance/canonical work.
- `work/orchestration/tasks/*.md` — detailed task handoffs that must survive chat/session loss.
- `work/parallel_state.json` — live translation-review gate and worker protocol routing.
- `work/translation_progress.json` — pinned source totals and canonical translation progress.
- `glossary/canonical_findings.json` — systemic worker findings awaiting canonical resolution; findings are blocking evidence, never automatic locks.

README progress is generated from these live sources and is human-facing only. Machine routing must read the underlying JSON/protocol files.

## Maintenance stages

Every serial maintenance task has an explicit `active_task.stage` in `work/orchestration/state.json`:

1. `domain_work` — substantive research/canonical/tooling work is still required;
2. `ready_for_finalize` — substantive domain work is done; only bounded cleanup/integration/verification remains;
3. `finalizing` — a finalizer currently owns/resumes that bounded finish work;
4. `complete` — task is finished and must no longer be claimed.

Legacy state with no `stage` is interpreted as `domain_work` only until it is normalized.

The purpose of these stages is to prevent a completed domain from being repeatedly re-claimed as if research/inventory were still unfinished.

## Maintenance lease

Serial repository-maintenance work must own `work/orchestration/maintenance_claim.json` before modifying the maintenance branch or advancing orchestration state.

A claim is valid only when:

- `status == "active"`;
- `task_id` matches the currently selected maintenance task/finding;
- `lease_expires_at` is still in the future;
- its claim stage is compatible with `active_task.stage`;
- every lease refresh after the initial claim contains NEW durable progress evidence.

Fresh claim/takeover rules:

1. fetch the current claim file and blob SHA;
2. if released/unclaimed/expired, update it with a unique worker ID/claim ID, current task ID, and current maintenance stage;
3. use the rolling lease from `work/worker_session_policy.json`;
4. checkpoint durable task changes before refreshing the lease;
5. never overwrite another worker's non-expired active claim;
6. at handoff, persist branch/task progress first, then mark the claim `released` with branch/head/checkpoint notes;
7. after completing the task and advancing orchestration state, mark the claim `complete` for the finished task. The next task may reset/reuse the file only after reading current orchestration state.

### Progress-backed heartbeat requirement

A maintenance heartbeat is not a clock tick. It is a claim refresh backed by new durable progress.

Before each refresh, persist at least one new durable artifact and record it in the claim as:

- `progress_token` — unique token that changed since the previous claim write;
- `progress_kind` — e.g. `branch_head`, `task_checkpoint`, `validation_run`, `sync_run`, `state_transition`;
- `progress_ref` — durable GitHub ref/SHA/run ID/path that proves the progress;
- `last_progress_at` — timestamp of that durable progress.

Valid examples include a new maintenance-branch head, a changed persistent task checkpoint, a newly completed validation/sync run whose result is checkpointed, or an orchestration-stage transition.

Invalid heartbeat: changing only `heartbeat_at` and `lease_expires_at`, or reusing the same `progress_token` merely because time passed.

If there is no new durable progress, do not refresh the lease. Continue read-only work only while the existing lease is valid; at handoff release the claim, otherwise let it expire so another worker can take over.

Waiting for CI is not by itself progress. A newly observed CI state/result becomes progress only when its run/job identity and result are persisted as a changed checkpoint.

If initial canonical hardening is blocking and another worker owns the active claim, do not start review/translation work behind the hardening gate.

## Finalization contract

`ready_for_finalize` and `finalizing` are deliberately narrow.

A finalizer MAY:

- remove temporary inventory/debug/staging artifacts;
- fix small acceptance discrepancies already identified by the task evidence;
- clean imports/formatting/build wiring needed for integration;
- rebase/cherry-pick/reconstruct clean permanent changes onto live `main` without overwriting unrelated work;
- run tests/validation;
- run production Sync and the required second unchanged no-op Sync;
- inspect representative regenerated contexts;
- persist completion evidence and advance orchestration.

A finalizer MUST NOT restart broad inventory, redo evidence gathering, or reopen the whole domain because the branch diverged. Branch divergence is an integration problem, not proof that domain research is incomplete.

Return from `finalizing` to `domain_work` only when finalization produces concrete evidence of a substantive unresolved domain defect. Persist the exact defect/evidence in the task file and state transition.

When substantive domain work becomes complete, the current owner should persist `stage = "ready_for_finalize"` and release the claim promptly instead of holding the same lease across indefinite cleanup/integration work.

## Phase 0 — initial canonical hardening

This phase is serial and blocking. The ordered domains are stored in `work/orchestration/state.json.roadmap`.

Current intended sequence:

1. Race terminology / classes / grades / racecourse / named-race identity;
2. Training / Support / progression;
3. Character / training-career UI;
4. Resources / gacha / shop;
5. Missions / rewards / events;
6. common system/UI vocabulary;
7. final high-frequency canonical conflict sweep.

Songs and staff/creator-credit hardening are intentionally not blocking domains. Isolated song/credit cases may be handled by ordinary review when encountered unless they reveal a genuinely systemic high-frequency defect.

Canonical-hardening rules:

- canonical-first: fix systemic terminology/context at its source;
- do not patch `localized_data/**` examples to hide systemic defects;
- use official Global terminology where verifiable, then official JP identity/organizer English forms, then strong established community terminology;
- zh-CN is a semantic bridge, not identity authority;
- prefer narrow/item-scoped invalidation for proper names/narrow mechanics when correctness permits;
- do not globally match generic prose just to reduce manual work;
- add positive and negative regression tests;
- permanent enforcement must be idempotent;
- remove temporary staging/inventory workflows/scripts before integration;
- full tests + plan rebuild + production Sync + second unchanged no-op Sync are required before a hardening domain is complete.

### Domain-work -> finalization transition

When substantive canonical decisions, permanent hardener/tooling, and permanent regression coverage are complete, but cleanup/integration/production verification remains:

1. checkpoint exact completed-domain evidence in the task file;
2. update `active_task.stage` from `domain_work` to `ready_for_finalize` using current blob SHA;
3. do not mark the roadmap item complete yet;
4. release the domain-work maintenance claim;
5. allow a fresh worker to claim the bounded finalization stage.

A finalizer then sets `stage = "finalizing"`, completes the finalization contract, and only after live verification marks the roadmap task `complete`.

When a domain fully completes, the finalizer must atomically update `work/orchestration/state.json`:

- mark the completed roadmap task `complete` with final main SHA and summary;
- set the completed task stage/status to `complete` in durable history/summary;
- activate the next pending canonical-hardening task with `stage = "domain_work"`;
- set its task file/branch if needed;
- keep `blocking_maintenance: true` until the final initial-hardening task is complete.

After the final initial hardening domain is clean, transition to `phase = "retrospective_translation_review"` and set `blocking_maintenance = false`.

## Canonical findings discovered during mass work

Review/translation workers must not silently choose a new project-wide terminology standard when they discover a systemic issue.

Expected flow:

1. worker records a structured canonical finding through the existing canonical-finding pipeline;
2. matching review items defer/block as designed instead of being accepted with arbitrary local wording;
3. a fresh `WORKER_START.md` session notices unresolved blocking findings;
4. a maintainer acquires the maintenance claim and verifies the concept;
5. maintainer locks/corrects canonical context or records an explicit defer/ignore decision;
6. production review-plan/context sync invalidates/reopens affected entries through existing context hashes;
7. ordinary workers resume under the corrected context.

Never blind-replace old translated text across the corpus. Canonical changes drive scoped review/invalidation; merge pipelines apply actual translated-string corrections.

## Phase 1 — retrospective translation review

Use `WORKER_25MIN.md` + `TRANSLATION_REVIEW.md`.

The current Audit Round 1 reviews all already-merged canonical translations under hardened context. Workers claim isolated review batches and may checkpoint/release partial decisions.

Do not open normal translation claims while `work/parallel_state.json.translation_review_gate.enabled == true`.

Systemic discoveries use the canonical-finding flow above.

Transition only when the live translation-review gate is cleared by production state, not merely when a worker says the audit is done.

## Phase 2 — retrospective UI review

After translation review clears, use `WORKER_25MIN.md` routing and `UI_REVIEW.md` while active assignable UI review remains.

UI review remains higher priority than untranslated content because real control fit/short-form issues create persistent regressions if ignored.

Transition to translation only when required UI review is no longer assignable/required according to live state.

## Phase 3 — translate current pinned queue

Use `PARALLEL_TRANSLATION.md` under the current pinned epoch.

Workers:

- claim isolated shards only;
- use the exact pinned `source_queue_git_commit`;
- checkpoint every configured interval;
- never edit canonical progress or `localized_data/**` directly;
- aggregation/merge workflows remain authoritative;
- regression/canonical/source-bridge guards must be obeyed.

The current source snapshot contains more entries than the initial queued wave. Therefore finishing the current queue is not project completion.

## Phase 4 — deferred-corpus queue expansion

Trigger condition:

- review/UI gates are clear;
- all entries in the current queued wave are canonically merged/covered;
- `work/translation_progress.json.deferred_entries > 0`.

This is serial maintenance and uses the maintenance claim/stage lifecycle above.

The maintainer must inspect the live queue-generation/source-batch tooling rather than inventing a new corpus. The next wave must:

- remain tied to the pinned source identity unless an explicit source-promotion task changes it;
- preserve already translated UIDs/fingerprints;
- promote a deterministic next tranche of deferred entries into claimable source batches/epoch metadata;
- keep completed Translation Memory/results reusable;
- update `queued_entries`, `deferred_entries`, batch/epoch metadata consistently;
- validate before publication;
- make the next wave claimable through the ordinary `PARALLEL_TRANSLATION.md` path.

Use bounded waves rather than trying to generate/commit an impractically huge one-shot worker queue if repository/tool limits make that unsafe. Repeat Phase 3 ↔ Phase 4 until `deferred_entries == 0` and translated/covered entries reach `source_total_entries` for the pinned corpus.

Do not silently change the pinned upstream source commit during queue expansion. Upstream promotion is a separate deliberate maintenance action.

## Phase 5 — post-completion audit rounds

Full source coverage is followed by deliberate full-corpus audits.

Minimum target:

1. post-completion Audit Round 2;
2. another full clean Audit Round 3 after Round 2 systemic corrections settle.

Increment `glossary/translation_audit_policy.json.audit_round` only as part of an explicit full-pass transition. Do not increment it for ordinary canonical edits during a round.

Each round must regenerate its review context/plan and complete through normal review merge state. Systemic findings still use canonical-first handling.

A further round is required if a late systemic correction makes the preceding full pass materially stale.

## Phase 6 — final verification/release

Terminal conditions include all of the following:

- pinned `source_total_entries` fully covered;
- no deferred pinned-source entries remain;
- required full-corpus translation audit rounds are clean;
- required UI review is clean/complete;
- no unresolved high-priority canonical finding remains without explicit defer/ignore rationale;
- tests/validation pass;
- release workflow succeeds and release index is publishable;
- progress/orchestration state agrees with canonical repository state.

Then set `work/orchestration/state.json.phase = "complete"`, `terminal = true`, and record the final main/release verification SHA(s).

## State-transition safety

Only a worker whose selected protocol explicitly owns the serial maintenance task may advance `work/orchestration/state.json`.

Mass review/translation workers do not rewrite the roadmap.

Before every state transition:

1. refetch live `main` and relevant active plan/progress files;
2. verify the completion condition from repository evidence;
3. fetch current state blob SHA;
4. update with optimistic concurrency;
5. never erase unrelated concurrent progress.

## Session behavior

Use `work/worker_session_policy.json` for timing. For serial maintenance that cannot finish in one session, checkpoint branch/task evidence in GitHub and release the maintenance claim by handoff time. The next fresh worker resumes from repository state and the task file; it does not restart research.

Do not keep a serial task alive by periodic time-only heartbeats. A refresh without a new durable progress token violates the protocol and should be treated as stale coordination rather than evidence of useful work.

The desired human workflow remains one line forever:

> Run `tailolicon/hachimi-tl-vi/WORKER_START.md` from `main`.

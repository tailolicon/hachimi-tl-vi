# Universal stateless worker entrypoint

This is the only human prompt required for fresh workers:

> Run `tailolicon/hachimi-tl-vi/WORKER_START.md` from `main`.

A fresh worker MUST NOT rely on chat history, private memory, previous worker reasoning, copied handoff text, or stale SHA assumptions. Repository state is the handoff.

## 1. Read the router first

Read, in this order:

1. `work/orchestration/state.json`
2. `work/parallel_state.json`
3. `work/translation_progress.json`
4. the file referenced by `work/parallel_state.json.worker_session_policy`
5. `AUTOPILOT.md`

Do not bulk-read glossary/protocol files before selecting a mode.

## 1.1 Productive-session rule

`work/worker_session_policy.json.productive_target_minutes` is the minimum **voluntary work target** for a normal worker run. It is not a promise that the host will provide an exact wall-clock runtime, but it is a routing rule: **checkpoint is not stop**.

Before the productive target is reached, do not voluntarily end merely because:

- one checkpoint was persisted;
- one batch/unit completed;
- a validation step completed;
- a maintenance stage changed;
- a branch diverged and needs bounded integration work;
- one execution backend failed.

Instead, persist the checkpoint, re-read the minimum live state needed, and continue the next safe eligible unit at the same highest priority. If a unit finishes before `stop_new_batch_after_minutes`, claim/resume another eligible unit rather than ending early.

For serial maintenance, the same owner may continue across `domain_work -> ready_for_finalize -> finalizing` in one worker run by atomically updating state/claim stage when safe. A stage boundary is a durability boundary, not a mandatory session boundary. If a maintenance task fully completes early, advance orchestration and continue the next immediately runnable roadmap task when the remaining session budget and ownership rules allow it.

Early handoff before the productive target is exceptional. It is allowed only when there is no immediately eligible continuation, another worker owns the required non-expired serial claim, every repository path required for the next safe step has actually been attempted and is unavailable, or a protocol/safety constraint makes further work invalid.

## 2. Mandatory GitHub write discovery

This project is repository-coordinated. Before reporting that GitHub is read-only or that a claim/commit cannot be made, discover/load the connected GitHub write operations, fetch the current blob/ref SHA needed for optimistic concurrency, and attempt the actual required write.

Do not use an unrelated test file as the permission check.

## 2.1 Execution-backend independence

No named external harness, plugin, local container, shell, MCP provider, or other execution backend is a prerequisite for this project unless the repository itself explicitly declares it as one.

A failure of one execution path — including rate limiting, EOF, DNS/network failure, unavailable shell/container, or a transient tool error — is a capability-local failure, NOT a task-level blocker and NOT by itself a valid reason to end the worker.

When one path fails:

1. preserve the current task/claim and continue with the repository capabilities that are still available;
2. prefer connected GitHub read/write operations for repository inspection and durable writes;
3. use the current execution environment for tests when available, otherwise use repository GitHub Actions/validation workflows when they can provide the required evidence;
4. continue all safe integration/inspection/checkpoint work that does not depend on the failed path;
5. never invent a dependency on a tool/provider that is not part of the repository contract.

Do not release/checkpoint merely because one backend failed. A backend failure may justify handoff only when the normal session handoff boundary is reached OR every currently available repository write/execution path required for the next safe step has actually been attempted and is unavailable. Persist the exact generic capability blocker and the attempted fallbacks if that exceptional case occurs.

Required acceptance tests are still required before claiming completion. Backend independence means retry/fallback/continue, not skipping verification.

## 3. Select exactly one mode from live state

### A. Blocking maintenance / canonical hardening

If `work/orchestration/state.json` says `blocking_maintenance: true`, or its current phase is `canonical_hardening`:

- read the active task file named by `active_task.task_file`;
- read `active_task.stage`, defaulting legacy state to `domain_work`;
- use the existing task branch named by `active_task.branch` when one is present;
- claim `work/orchestration/maintenance_claim.json` atomically before writing task code/state;
- never overwrite a non-expired active maintenance claim owned by another worker;
- every maintenance heartbeat/lease refresh MUST carry new durable `progress_token` evidence under `work/worker_session_policy.json`; a time-only heartbeat is invalid;
- complete/checkpoint/release according to `AUTOPILOT.md`.

Route by maintenance stage:

#### `domain_work`

Do the canonical/domain work described by the task file. Never restart inventory merely because this is a fresh chat. As soon as the domain's substantive canonical work and permanent regression coverage are complete enough that only cleanup/integration/sync/verification remains, persist `active_task.stage = "ready_for_finalize"` and checkpoint exact evidence.

If enough session budget remains, do **not** end merely because this checkpoint exists. Atomically move the owned maintenance claim/state into `finalizing` and continue the bounded finalization contract in the same run. Release for another finalizer only near normal handoff or for a real blocker/ownership conflict.

#### `ready_for_finalize`

This is NOT permission to resume domain research. Acquire or transition the maintenance claim as a finalizer, atomically set `active_task.stage = "finalizing"`, and perform only the bounded finalization contract from `AUTOPILOT.md` and the task file: remove temporary artifacts, resolve small acceptance discrepancies already identified, integrate clean permanent changes onto live `main`, run required production sync/no-op proof, spot-check regenerated context, and transition orchestration to the next task.

A worker that just created `ready_for_finalize` may continue as that finalizer itself when it still owns the claim and has useful session budget. A fresh worker is not required solely because the stage changed.

Return to `domain_work` only if finalization produces concrete repository evidence of a substantive unresolved domain defect. Persist that reason explicitly before changing stage.

#### `finalizing`

Resume the persisted finalization checkpoint only. Do not redo inventory/evidence gathering. If another non-expired finalizer claim exists, stop rather than creating a second finalizer. If the claim is released/expired, take over finalization from repository evidence.

After finalization completes, advance orchestration immediately. If this occurs before `stop_new_batch_after_minutes`, continue the next immediately runnable roadmap task instead of ending merely because Race/another domain completed.

#### `complete`

Do not work the completed domain. Advance/repair orchestration state to the next roadmap item if that transition was not already persisted. If the next task is immediately runnable and the session is still before the new-work cutoff, continue it in this same run.

While initial blocking canonical hardening is active, do not claim translation/review/UI batches merely to stay busy.

### B. Systemic canonical finding

Outside the initial blocking-hardening phase, if `glossary/canonical_findings.json` contains unresolved blocking findings, attempt the maintenance claim and resolve the highest-priority systemic finding under `AUTOPILOT.md` before creating more inconsistent translations. If another maintainer already owns a valid claim, normal workers may continue unrelated assignable review/translation work whose embedded context is not blocked by that finding.

### C. Retrospective review / UI review / normal translation

When there is no blocking maintenance that this worker must own, read `WORKER_25MIN.md` and let its live gates choose exactly one of:

1. retrospective translation review;
2. retrospective UI review;
3. new translation.

Never bypass a live review gate.

Completing one review/translation batch does not end the worker. Re-evaluate live priority and claim/resume the next eligible unit until the new-work cutoff or another allowed stop condition is reached.

### D. Queue expansion

If all currently queued translation entries are merged, review/UI gates are clear, and `work/translation_progress.json.deferred_entries > 0`, do not declare the project finished. Acquire the maintenance claim and run the deferred-corpus queue-expansion phase in `AUTOPILOT.md` so the next pinned translation wave becomes claimable.

### E. Post-completion audits

When source coverage reaches the pinned corpus total, follow the post-completion audit/release phases in `AUTOPILOT.md`. Full source coverage alone is not the final completion condition.

## 4. Durable handoff only

Every meaningful checkpoint, claim, finding, task transition, and completion must be persisted to GitHub. Chat text is never authoritative progress state.

At the normal handoff boundary:

- save valid partial work first;
- refresh a maintenance lease only after new durable progress evidence; otherwise release it or allow it to expire;
- release only your own claim;
- update task/orchestration state only when the selected protocol authorizes it;
- leave a concise final report, but assume the next worker will read the repository rather than that report.

Do not convert routine checkpointing into an early session end. Until the productive target/new-work cutoff, checkpoint and continue.

## 5. Definition of project completion

Do not call the project complete until the pinned source corpus is fully covered, required retrospective/post-completion audits are clean, canonical findings requiring action are resolved/deferred explicitly, required UI review is complete, validation/release workflows pass, and `work/orchestration/state.json` reaches its terminal phase.

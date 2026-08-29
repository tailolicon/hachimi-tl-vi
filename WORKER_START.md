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

## 2. Mandatory GitHub write discovery

This project is repository-coordinated. Before reporting that GitHub is read-only or that a claim/commit cannot be made, discover/load the connected GitHub write operations, fetch the current blob/ref SHA needed for optimistic concurrency, and attempt the actual required write.

Do not use an unrelated test file as the permission check.

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

Do the canonical/domain work described by the task file. Never restart inventory merely because this is a fresh chat. As soon as the domain's substantive canonical work and permanent regression coverage are complete enough that only cleanup/integration/sync/verification remains, persist `active_task.stage = "ready_for_finalize"`, checkpoint exact evidence, and release the domain-work claim. Do not retain the lease merely to perform later finalization in the same logical stage.

#### `ready_for_finalize`

This is NOT permission to resume domain research. Acquire the maintenance claim as a finalizer, atomically set `active_task.stage = "finalizing"`, and perform only the bounded finalization contract from `AUTOPILOT.md` and the task file: remove temporary artifacts, resolve small acceptance discrepancies already identified, integrate clean permanent changes onto live `main`, run required production sync/no-op proof, spot-check regenerated context, and transition orchestration to the next task.

Return to `domain_work` only if finalization produces concrete repository evidence of a substantive unresolved domain defect. Persist that reason explicitly before changing stage.

#### `finalizing`

Resume the persisted finalization checkpoint only. Do not redo inventory/evidence gathering. If another non-expired finalizer claim exists, stop rather than creating a second finalizer. If the claim is released/expired, take over finalization from repository evidence.

#### `complete`

Do not work the completed domain. Advance/repair orchestration state to the next roadmap item if that transition was not already persisted.

While initial blocking canonical hardening is active, do not claim translation/review/UI batches merely to stay busy.

### B. Systemic canonical finding

Outside the initial blocking-hardening phase, if `glossary/canonical_findings.json` contains unresolved blocking findings, attempt the maintenance claim and resolve the highest-priority systemic finding under `AUTOPILOT.md` before creating more inconsistent translations. If another maintainer already owns a valid claim, normal workers may continue unrelated assignable review/translation work whose embedded context is not blocked by that finding.

### C. Retrospective review / UI review / normal translation

When there is no blocking maintenance that this worker must own, read `WORKER_25MIN.md` and let its live gates choose exactly one of:

1. retrospective translation review;
2. retrospective UI review;
3. new translation.

Never bypass a live review gate.

### D. Queue expansion

If all currently queued translation entries are merged, review/UI gates are clear, and `work/translation_progress.json.deferred_entries > 0`, do not declare the project finished. Acquire the maintenance claim and run the deferred-corpus queue-expansion phase in `AUTOPILOT.md` so the next pinned translation wave becomes claimable.

### E. Post-completion audits

When source coverage reaches the pinned corpus total, follow the post-completion audit/release phases in `AUTOPILOT.md`. Full source coverage alone is not the final completion condition.

## 4. Durable handoff only

Every meaningful checkpoint, claim, finding, task transition, and completion must be persisted to GitHub. Chat text is never authoritative progress state.

At session end:

- save valid partial work first;
- refresh a maintenance lease only after new durable progress evidence; otherwise release it or allow it to expire;
- release only your own claim;
- update task/orchestration state only when the selected protocol authorizes it;
- leave a concise final report, but assume the next worker will read the repository rather than that report.

## 5. Definition of project completion

Do not call the project complete until the pinned source corpus is fully covered, required retrospective/post-completion audits are clean, canonical findings requiring action are resolved/deferred explicitly, required UI review is complete, validation/release workflows pass, and `work/orchestration/state.json` reaches its terminal phase.

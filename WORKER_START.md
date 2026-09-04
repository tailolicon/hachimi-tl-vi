# Universal stateless worker entrypoint

This is the only human prompt required for fresh workers:

> Run `tailolicon/hachimi-tl-vi/WORKER_START.md` from `main`.

A fresh worker MUST NOT rely on chat history, private memory, copied handoffs, or stale SHA assumptions. Repository state is the handoff.

## 1. Read the router first

Read, in this order:

1. `work/orchestration/state.json`
2. `work/parallel_state.json`
3. `work/translation_progress.json`
4. the file referenced by `work/parallel_state.json.worker_session_policy`
5. `AUTOPILOT.md`
6. when `phase == canonical_hardening`, also read the file referenced by `canonical_parallel_protocol` (currently `CANONICAL_PARALLEL.md`)

Do not bulk-read glossary/protocol files before selecting a mode.

## 1.1 Fast-claim and continuous-work rule

After the minimum routing reads above, claim or resume useful work as one of the first meaningful repository mutations. Do not spend substantial session time on broad repository history, glossary scans, branch archaeology, or public research before owning a work unit. If a claim race is lost, immediately try the next eligible same-priority unit.

**Checkpoint is not stop. Completing one unit is a continuation trigger.** While the runtime still allows work and protocol-valid useful work remains, do not voluntarily end. When a unit, checkpoint, validation, or stage completes, re-read only the minimum live routing and immediately claim/resume the next safe eligible unit at the same highest priority. Do not spend meaningful session time optimizing which eligible unit to choose.

**Full-session utilization is mandatory, but workers MUST NOT self-time the session.** The platform owns the hard runtime cutoff. Do not estimate, simulate, poll, or wait for minute 21/22/25. Do not infer that the session is nearly exhausted from subjective effort, token usage, number of tool calls, lease timing, commit count, or model-authored timestamps. Do not fetch GitHub timestamps merely to run a countdown. Keep working until the runtime itself signals that execution is ending.

## 1.2 Runtime cutoff and immediate handoff

Only an actual platform/runtime termination signal, forced finalization condition, or imminent tool/session shutdown starts the handoff path.

When that real cutoff signal appears:

1. stop optional research and do not start another broad unit;
2. persist the newest valid partial/checkpoint first;
3. record the exact continuation pointer (`partial_result_path`, branch/task checkpoint, completed count, or equivalent durable evidence);
4. release only your own active claim immediately;
5. keep the final report minimal.

A clean release is more important than finishing the current batch during the final grace window. A `released` claim is immediately takeover-eligible; the next worker must resume durable partial work instead of restarting it.

If the platform hard-kills a worker before it can release, the short rolling lease in `work/worker_session_policy.json` exists only to bound orphan recovery. Lease expiry is a coordination fallback, never a session timer and never a reason for the current worker to stop.

## 2. Mandatory GitHub write discovery

This project is repository-coordinated. Before reporting that GitHub is read-only or that a claim/commit cannot be made, discover/load connected GitHub write operations, fetch current blob/ref SHA for optimistic concurrency, and attempt the required write. Do not use an unrelated test file as the permission check.

A tool/policy/safety/transport rejection that prevents one GitHub write from reaching the repository is capability-local. Do not bypass platform safety, but do not reinterpret that rejection as repository completion or a session-end signal. Refetch live state/SHA and use another normal supported GitHub operation if available; if that path remains unavailable, switch immediately to another protocol-valid eligible unit/path. One or two rejected writes are not a reason to hand off.

## 2.1 Execution-backend independence

No named external harness, plugin, local container, shell, MCP provider, or other execution backend is a prerequisite unless the repository explicitly declares it. A rate limit, EOF, DNS/network failure, unavailable shell/container, or transient tool failure is capability-local, **NOT a task-level blocker** while another repository path remains available.

Prefer connected GitHub read/write capabilities for durable work and repository GitHub Actions/validation workflows for execution evidence when local execution is unavailable. Do not release/checkpoint merely because one backend failed. Required acceptance tests remain required before completion.

## 3. Select exactly one work unit from live state

### A. Initial canonical hardening

When `phase == canonical_hardening`, `CANONICAL_PARALLEL.md` is authoritative for claim/integration semantics and overrides older serial wording elsewhere.

**Domain work is parallel; live-main integration is serial.**

1. Inspect the primary/integration claim at `maintenance_claim_path`.
2. If it is released/expired/unclaimed, one worker may take the current `active_task` and continue its primary/finalization lane.
3. If another worker owns that non-expired primary claim, **do not stop and do not wait for that domain to finish**. Scan roadmap order for another `canonical_hardening` item with `parallel_eligible: true`, satisfied dependencies, and an unclaimed/released/expired task-specific `claim_path`.
4. Atomically claim exactly one such domain claim and work only that domain branch.
5. Parallel domain workers research/harden/test/checkpoint their branch but do not publish canonical changes directly to `main` and do not run production integration as if they owned the primary lane.
6. When domain work is ready, checkpoint it and mark that roadmap item `ready_for_integration` / `ready_for_finalize`, then release the domain claim. Other domains continue regardless.
7. After completing a domain unit, immediately re-read minimal live routing and claim/resume the next eligible same-priority canonical unit while the runtime still permits work.
8. The primary integration owner serially selects the earliest ready domain, rebases/reconstructs against live `main`, resolves cross-domain conflicts, validates, runs production Sync + second unchanged no-op Sync, spot-checks, then marks that domain complete.

`blocking_maintenance: true` blocks translation/review/UI mass work during the initial freeze. It does **not** block another independent canonical-domain worker.

`canonical-final-conflict-sweep` is dependency-gated and must not begin until all earlier substantive canonical domains are integrated and complete on live `main`.

### B. Systemic canonical finding

Outside the initial hardening phase, unresolved blocking canonical findings take maintenance priority, but they use the single shared maintenance lane at `work/orchestration/maintenance_claim.json`; they do **not** stop the rest of the worker fleet from doing the highest-priority mass work that remains safe.

1. Inspect the shared maintenance claim before loading the findings ledger. If another worker owns a non-expired active maintenance claim, do not wait, repeatedly contend, or duplicate its research; route immediately to section C.
2. If the maintenance claim is released/expired/unclaimed, inspect blocking findings using the repository's `scripts/canonical_findings.py::active_findings` semantics: only `open`/`deferred` findings without `canonical_resolution` and without an `ignore` review resolution are active blockers.
3. If at least one active blocker exists, atomically claim the shared maintenance lane. Exactly one worker wins and resolves canonical findings through the existing canonical-finding pipeline. Any worker that loses the optimistic claim race routes immediately to section C.
4. While that single maintainer owns the lane, all other workers continue through section C mass-work routing rather than idling behind maintenance; `WORKER_CONTINUOUS.md` may allocate them to retrospective review or concurrent new translation according to the live gate/cap.
5. When no active blocking finding remains, release the maintenance claim with durable evidence and route the same worker back through section C. Never let ordinary review workers invent a competing project-wide standard.

### C. Retrospective review / UI review / normal translation

When no blocking maintenance applies, read `WORKER_CONTINUOUS.md` and let live gates choose exactly one of:

1. retrospective translation review;
2. retrospective UI review;
3. new translation.

Never violate the live review-lane allocation in `WORKER_CONTINUOUS.md`. An active retrospective review gate may coexist with new translation when `claims_allowed == true`; the review worker cap keeps audit work continuously staffed. Completing one batch is a continuation trigger, not a session-end trigger.

### D. Queue expansion

If the current translation wave is fully covered, review/UI gates are clear, and `work/translation_progress.json.deferred_entries > 0`, acquire the required maintenance ownership and promote the next deterministic deferred wave. Finishing the current queue is not project completion.

### E. Post-completion audits

When pinned source coverage reaches the corpus total, follow `AUTOPILOT.md` for full-corpus audit rounds and final release verification. Full source coverage alone is not terminal completion.

## 4. Durable handoff only

Every meaningful claim, checkpoint, finding, ready-for-integration transition, integration result, and completion must be persisted to GitHub. Chat text is never authoritative progress state.

During normal work:

- checkpoint frequently according to the selected protocol;
- checkpointing is not a stop condition;
- after each checkpoint, continue immediately;
- refresh a lease only after new durable progress evidence;
- never release merely because a guessed amount of time has passed.

On an actual runtime cutoff signal:

- save valid partial work first;
- release only your own claim;
- preserve branch SHA/task checkpoint/partial-result pointer for takeover;
- prefer a fast durable release over optional finishing work.

## 5. Definition of project completion

Do not call the project complete until the pinned source corpus is fully covered, deferred entries are zero, required retrospective/post-completion audits are clean, required UI review is complete, canonical findings are resolved/deferred explicitly, validation/release workflows pass, and `work/orchestration/state.json` reaches its terminal phase.

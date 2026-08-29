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

## 1.1 Productive-session rule

`work/worker_session_policy.json.productive_target_minutes` is the minimum voluntary work target. **Checkpoint is not stop.** Before that target, do not voluntarily end merely because one checkpoint, batch, validation, stage transition, branch divergence, or backend failure occurred. Persist progress, re-read the minimum live state, and continue the next safe eligible unit until the new-work cutoff or a real blocker.

## 2. Mandatory GitHub write discovery

This project is repository-coordinated. Before reporting that GitHub is read-only or that a claim/commit cannot be made, discover/load connected GitHub write operations, fetch current blob/ref SHA for optimistic concurrency, and attempt the required write. Do not use an unrelated test file as the permission check.

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
7. The primary integration owner serially selects the earliest ready domain, rebases/reconstructs against live `main`, resolves cross-domain conflicts, validates, runs production Sync + second unchanged no-op Sync, spot-checks, then marks that domain complete.

`blocking_maintenance: true` blocks translation/review/UI mass work during the initial freeze. It does **not** block another independent canonical-domain worker.

`canonical-final-conflict-sweep` is dependency-gated and must not begin until all earlier substantive canonical domains are integrated and complete on live `main`.

### B. Systemic canonical finding

Outside the initial hardening phase, unresolved blocking canonical findings take maintenance priority. Resolve them through the canonical-finding pipeline; never let ordinary workers invent a competing project-wide standard.

### C. Retrospective review / UI review / normal translation

When no blocking maintenance applies, read `WORKER_25MIN.md` and let live gates choose exactly one of:

1. retrospective translation review;
2. retrospective UI review;
3. new translation.

Never bypass a live review gate. Completing one batch is a continuation trigger, not a session-end trigger.

### D. Queue expansion

If the current translation wave is fully covered, review/UI gates are clear, and `work/translation_progress.json.deferred_entries > 0`, acquire the required maintenance ownership and promote the next deterministic deferred wave. Finishing the current queue is not project completion.

### E. Post-completion audits

When pinned source coverage reaches the corpus total, follow `AUTOPILOT.md` for full-corpus audit rounds and final release verification. Full source coverage alone is not terminal completion.

## 4. Durable handoff only

Every meaningful claim, checkpoint, finding, ready-for-integration transition, integration result, and completion must be persisted to GitHub. Chat text is never authoritative progress state.

At the normal handoff boundary:

- save valid partial work first;
- refresh a lease only after new durable progress evidence;
- release only your own claim;
- preserve branch SHA/task checkpoint for takeover;
- never convert routine checkpointing into an early session end.

## 5. Definition of project completion

Do not call the project complete until the pinned source corpus is fully covered, deferred entries are zero, required retrospective/post-completion audits are clean, required UI review is complete, canonical findings are resolved/deferred explicitly, validation/release workflows pass, and `work/orchestration/state.json` reaches its terminal phase.

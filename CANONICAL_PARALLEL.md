# Parallel canonical-hardening protocol

This protocol governs Phase 0 canonical hardening and overrides any older wording that implies one domain must fully finish before another domain may begin.

## Core rule

**Domain work is parallel. Integration is serial.**

Multiple canonical domains may be researched, hardened, tested, and checkpointed concurrently on separate branches. Only the operation that publishes canonical changes to live `main` and runs production Sync/no-op verification is serialized.

`blocking_maintenance: true` blocks mass translation/review/UI work during the initial hardening freeze. It does **not** block another canonical-domain worker from working on an independent eligible domain.

## Coordination files

- `work/orchestration/state.json` — roadmap, primary/integration lane, parallelism policy.
- `work/orchestration/maintenance_claim.json` — the primary/integration lane claim. This remains the single writer for live-main canonical integration and production Sync transitions.
- `work/orchestration/domain_claims/<task-id>.json` — independent domain-work claims.
- `work/orchestration/tasks/*.md` — persistent domain scope/handoff.

A worker must never use the primary `maintenance_claim.json` merely because another independent domain is available. Parallel domain workers use their task-specific claim file.

## Worker routing during canonical_hardening

A fresh `WORKER_START.md` worker routes in this order:

1. Read live state and the primary `maintenance_claim.json`.
2. If the primary/integration lane is takeover-eligible, one worker may own it and continue the current `active_task`.
3. If another worker already owns that non-expired primary claim, **do not stop**. Scan roadmap order for another canonical item with `parallel_eligible: true` whose dependencies are satisfied and whose domain claim is unclaimed/released/expired.
4. Atomically claim exactly one `work/orchestration/domain_claims/<task-id>.json` using its current blob SHA.
5. Use/create only that task's branch and perform its `domain_work` there.
6. If no primary lane and no parallel domain is safely claimable, then and only then may canonical work be temporarily unavailable.

This means a Training worker, Character/UI worker, Resources/Gacha worker, Missions worker, and Common-UI worker may all be active at once on independent branches.

## Domain-claim rules

A domain claim is task-scoped. It uses the same progress-backed lease principles as maintenance claims:

- one active owner per domain;
- optimistic-concurrency writes;
- new durable progress before lease refresh;
- no time-only heartbeat;
- released/expired claims are immediately takeover-eligible;
- checkpoint branch SHA + task evidence before handoff.

A domain worker may edit its own branch and its own domain claim. It must not publish canonical changes directly to `main`, advance unrelated roadmap items, or run production integration as if it owned the primary lane.

## Branch rules

Each domain has a deterministic branch named by roadmap `branch` or `suggested_branch`.

A parallel worker:

- branches from the then-live `main` when the branch does not exist;
- resumes the existing domain branch when it does exist;
- never creates a second branch just because live main advanced;
- records divergence as an integration concern, not a reason to redo domain research.

Because other domains may integrate while a branch is in progress, final integration must always compare/rebase/reconstruct against current `main` and preserve unrelated canonical changes.

## Domain-work completion

When substantive domain research/canonical decisions/permanent hardener/regression coverage are complete enough that only cleanup/integration/production verification remains, the parallel domain worker must:

1. checkpoint exact branch SHA and evidence;
2. update that roadmap item's `status` to `ready_for_integration` and `stage` to `ready_for_finalize` with optimistic concurrency;
3. release its task-specific domain claim;
4. **not** wait for that domain to be integrated before other eligible domains continue their own work.

`ready_for_integration` means the branch is queued for the serial integration lane; it is not a global blocker for other canonical domain work.

## Serial integration lane

Only one integration/finalization owner may publish canonical changes to `main` at a time. It owns `work/orchestration/maintenance_claim.json`.

The integration owner selects work deterministically:

1. continue the current `active_task` if it is already in `ready_for_finalize`/`finalizing`;
2. otherwise choose the earliest roadmap item in `ready_for_integration` whose dependencies are satisfied;
3. if none is ready, the primary lane may continue one unfinished eligible domain, while other workers remain free to work other domains in parallel.

For each domain integration:

- fetch live main;
- compare with the domain branch;
- preserve already-integrated changes from other domains;
- resolve cross-domain canonical conflicts explicitly;
- remove TEMP artifacts;
- run required full validation;
- rebuild review context;
- run production Sync;
- run the second unchanged Sync/no-op proof;
- spot-check representative positive/negative contexts;
- then mark that roadmap item `complete`.

A domain branch being ready does not allow a parallel domain worker to bypass this integration lock.

## Final conflict sweep dependency

`canonical-final-conflict-sweep` is intentionally **not** parallel with the substantive domain hardeners. It depends on completion/integration of all earlier initial canonical domains because its purpose is to detect cross-domain split-brain state after those domains have landed.

The sweep becomes claimable only after Race, Training/Support, Character/Training UI, Resources/Gacha/Shop, Missions/Events, and Common UI/System are complete on live main.

## Transition to mass audit

Initial canonical hardening remains a quality gate for mass review/translation. Phase 0 ends only when every required canonical roadmap item, including the final conflict sweep, is complete.

Then the integration owner sets `blocking_maintenance = false` and transitions to retrospective translation Audit Round 1.

## Safety invariant

Parallelism must increase throughput without creating multiple canonical truths:

- research/hardening/test branches: parallel;
- domain claims: independent;
- live-main canonical integration: one at a time;
- production Sync/state transition: one at a time;
- canonical conflicts: resolved explicitly at integration, never by last-writer-wins.

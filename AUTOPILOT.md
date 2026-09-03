# Repository autopilot lifecycle

`WORKER_START.md` is the only human entrypoint. Repository state is authoritative; chat history is not.

## Global priority

1. initial canonical hardening / canonical integration;
2. unresolved systemic canonical findings that would propagate inconsistency;
3. retrospective translation review;
4. retrospective UI review;
5. normal translation of the current pinned wave;
6. deterministic expansion of deferred pinned-source content;
7. post-completion full-corpus audits;
8. final release verification.

Quality gates outrank raw translation percentage.

## Productive-session utilization

Use `work/worker_session_policy.json` as timing authority. A durable checkpoint is not a stop signal. Completing one unit, stage, validation, or task means re-read the minimum live state and continue the next safe eligible unit while before the new-work cutoff.

Never idle merely to reach the handoff minute.

A backend/plugin/container failure is capability-local. Follow the execution-backend-independent fallback rules in `WORKER_START.md` and policy; required acceptance evidence may move to GitHub Actions rather than being skipped.

## Persistent control files

- `WORKER_START.md` — universal router.
- `work/orchestration/state.json` — project phase, roadmap, primary integration lane and parallelism policy.
- `CANONICAL_PARALLEL.md` — authoritative initial canonical parallel-domain protocol.
- `work/orchestration/maintenance_claim.json` — primary/live-main integration lease.
- `work/orchestration/domain_claims/*.json` — independent canonical domain-work leases.
- `work/orchestration/tasks/*.md` — persistent task scopes/handoffs.
- `work/parallel_state.json` — live review/translation gate routing.
- `work/translation_progress.json` — pinned source totals and translation progress.
- `glossary/canonical_findings.json` — systemic findings; blocking evidence, never automatic canonical locks.

README is human-facing progress only. Machine routing reads the JSON/protocol files above.

## Lease invariant

Every maintenance/domain lease is progress-backed:

- one active owner per claim file;
- optimistic concurrency on every write;
- lease refresh only after new durable progress;
- `progress_token`, `progress_kind`, `progress_ref`, `last_progress_at` identify that durable evidence;
- a time-only heartbeat is invalid;
- released/expired claims are takeover-eligible;
- persist branch/result/checkpoint before handoff.

Do not overwrite another worker's non-expired claim.

## Phase 0 — initial canonical hardening

**Domain work is parallel. Integration is serial.** `CANONICAL_PARALLEL.md` is authoritative for this phase.

`blocking_maintenance = true` blocks mass translation/review/UI work until the initial canonical freeze is complete. It does not stop independent canonical-domain workers.

### Parallel domain lane

If the primary maintenance claim is already owned by another worker, a fresh canonical worker must scan roadmap order for another dependency-satisfied item with `parallel_eligible: true` and a takeover-eligible task-specific `claim_path`.

A parallel domain worker:

1. atomically claims that domain file;
2. resumes/creates the deterministic domain branch;
3. performs only that domain's inventory/evidence/canonical hardening/permanent tests;
4. never patches `localized_data/**` examples to hide systemic defects;
5. never publishes canonical changes directly to live `main`;
6. checkpoints branch SHA/evidence throughout;
7. when substantive work is ready, sets only that roadmap item to `status = ready_for_integration` and `stage = ready_for_finalize`, then releases the domain claim.

Another domain does not wait for this integration. This is the core throughput rule.

### Primary integration lane

Only the owner of `work/orchestration/maintenance_claim.json` may serialize canonical publication to live `main` and completion transitions.

It chooses work deterministically:

1. continue the current `active_task` if already `ready_for_finalize`/`finalizing`;
2. otherwise select the earliest dependency-satisfied `ready_for_integration` roadmap item;
3. if none is ready, it may continue one unfinished canonical domain as the primary lane while other workers remain free to claim other eligible domains.

For each integration:

- fetch live main again;
- compare/rebase/reconstruct the domain branch without erasing concurrent main changes;
- resolve cross-domain canonical conflicts explicitly, never last-writer-wins;
- remove TEMP inventory/debug/staging artifacts;
- run full validation;
- rebuild retrospective review context;
- run production Sync;
- run the second unchanged production Sync and prove semantic no-op;
- inspect representative positive and negative contexts;
- only then mark that domain `complete`.

Branch divergence is an integration problem, not evidence that domain research must restart.

### Initial domain order vs parallelism

Roadmap order remains the deterministic integration/priority order, not a requirement that research wait serially.

The substantive domains may overlap in time:

- Training / Support / progression;
- Character / training-career UI;
- Resources / gacha / shop;
- Missions / rewards / events;
- Common system/UI.

Race is already a predecessor domain when marked complete.

`canonical-final-conflict-sweep` is intentionally not parallel-eligible. It depends on all preceding substantive canonical domains being complete on live main, because it checks their combined state for split-brain terminology, overmatching, hidden legacy locks, and missing negative coverage.

### Canonical hardening rules

Across all domains:

- canonical-first systemic fixes;
- official Global terminology where verifiable, then official JP/organizer identity, then strong established community usage;
- zh-CN is a semantic bridge, not identity authority;
- narrow/item-scoped invalidation for proper names/narrow mechanics where correctness permits;
- generic prose must not match named/system concepts merely because words overlap;
- positive and negative regression tests;
- permanent enforcement idempotent;
- no TEMP hardening artifacts on main;
- canonical changes reopen affected prior translations through context/review invalidation rather than blind corpus replacement.

### Phase-0 completion

When all substantive domains are integrated and complete, run the final conflict sweep serially. Its completion requires full validation, production Sync, representative positive/negative checks, second unchanged Sync no-op proof, and no known high-frequency systemic conflict left without explicit defer rationale.

Then the integration owner atomically:

- sets `blocking_maintenance = false`;
- sets `phase = retrospective_translation_review`;
- marks `canonical-final-conflict-sweep` complete;
- advances the roadmap to Audit Round 1.

## Canonical findings during mass work

Review/translation workers do not choose a new project-wide standard ad hoc.

Canonical-finding maintenance is a **single nonblocking lane** during mass review. `work/orchestration/maintenance_claim.json` is the ownership lock: one eligible worker may own it and resolve active findings, while every other worker immediately continues the highest-priority safe review/UI work. A worker that observes another non-expired maintenance owner or loses the optimistic claim race must not wait or repeatedly contend. It falls through to ordinary mass work. Only findings returned by `scripts/canonical_findings.py::active_findings` are routing blockers; a ledger row that still says `status: open` but already has `canonical_resolution` is not active maintenance work.

Expected loop:

1. worker emits structured canonical finding;
2. matching review items defer/block;
3. a maintainer verifies the concept;
4. maintainer locks/corrects canonical context or records explicit defer/ignore;
5. production plan/context sync invalidates affected items;
6. ordinary workers resume under corrected context.

Never blind-rewrite the corpus from a finding.

## Phase 1 — retrospective translation Audit Round 1

Use `WORKER_25MIN.md` + `TRANSLATION_REVIEW.md`.

- review all already-merged canonical translations under hardened context;
- do not open normal translation claims while the translation-review gate is enabled;
- completing one review batch is a continuation trigger;
- systemic discoveries use the canonical-finding loop;
- transition only when the live production gate clears.

## Phase 2 — retrospective UI review

After translation review clears, use `WORKER_25MIN.md` + `UI_REVIEW.md` while required UI work remains. UI review outranks untranslated content until the live UI gate is clear.

## Phase 3 — translate current pinned wave

Use `PARALLEL_TRANSLATION.md` under the pinned source epoch.

Workers claim isolated shards, obey canonical/context guards, checkpoint per policy, and never edit canonical progress or `localized_data/**` directly outside the merge pipeline.

Finishing the current wave is not project completion if deferred pinned entries remain.

## Phase 4 — deferred-corpus wave expansion

Trigger when review/UI gates are clear, the current wave is fully covered, and `deferred_entries > 0`.

Serial queue-maintenance must:

- remain tied to the pinned source identity unless a separate explicit source-promotion task changes it;
- preserve translated UIDs/fingerprints and reusable results;
- deterministically promote a bounded next tranche of deferred entries;
- update queue/deferred/batch/epoch metadata consistently;
- validate before publication;
- make the next wave claimable through ordinary translation workers.

Repeat Phase 3 ↔ Phase 4 until deferred entries are zero and pinned source coverage reaches the source total.

## Phase 5 — post-completion full-corpus audits

Full source coverage is followed by at least:

1. full-corpus Audit Round 2;
2. a clean full-corpus Audit Round 3 after Round-2 systemic corrections settle.

Increment `glossary/translation_audit_policy.json.audit_round` only on explicit full-pass transitions. If a late systemic correction materially stales the preceding pass, require another clean round.

## Phase 6 — final verification/release

Terminal conditions include:

- full pinned source coverage;
- zero deferred pinned-source entries;
- required full-corpus audit rounds clean;
- required UI review complete;
- no unresolved high-priority canonical finding without explicit defer/ignore rationale;
- tests/validation pass;
- release workflow succeeds and release index is publishable;
- orchestration/progress state agrees with canonical repository state.

Then set `work/orchestration/state.json.phase = complete`, `terminal = true`, and persist final main/release verification SHAs.

## State-transition safety

Before every state transition:

1. refetch live main and relevant progress/plan/claim files;
2. verify the transition condition from repository evidence;
3. fetch the current state blob SHA;
4. update with optimistic concurrency;
5. never erase unrelated concurrent progress.

Parallel domain workers may update only their own claim/checkpoint and their own roadmap readiness fields. Only the primary integration lane may publish live-main canonical integration completion or advance global phase gates.

## Human workflow

The desired human workflow remains one line forever:

> Run `tailolicon/hachimi-tl-vi/WORKER_START.md` from `main`.

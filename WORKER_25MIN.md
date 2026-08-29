# Stateless 25-minute mass-work protocol

`WORKER_START.md` is the universal top-level entrypoint for every fresh ChatGPT worker session on `tailolicon/hachimi-tl-vi`.

Use this file **only after `WORKER_START.md` delegates the session to ordinary mass work** because no blocking repository-maintenance/canonical-hardening task requires this worker. This protocol then selects exactly one of retrospective translation review, retrospective UI review, or new translation from live state.

Do not bypass `WORKER_START.md` to escape a blocking maintenance task or unresolved routing condition.

Do not rely on chat history, private memory, previous worker reasoning, or stale progress assumptions. `main` is the source of truth.

## Hard priority order

1. retrospective translation audit;
2. retrospective UI audit;
3. only then new untranslated content.

Never skip unfinished old-content audit merely to increase raw translation percentage.

## Startup hot path

Read `work/parallel_state.json` first, then the file referenced by `worker_session_policy`.

Do not load translation/UI/new-translation protocols in parallel. Select exactly one work mode from live state, then load only that mode's protocol and one batch/task.

After the minimum routing reads, claim/resume useful work immediately. A valid claim/resume should be one of the first meaningful repository mutations of the run. Do not perform deep repository analysis, broad glossary scans, branch archaeology, or public research before owning a work unit. If another worker wins a claim race, immediately try the next eligible same-priority unit.

## Mandatory GitHub write-capability discovery

This worker system is repository-coordinated. Claim, checkpoint, completion, heartbeat, and handoff state must be written to `main` through the connected GitHub capability available in the current session.

**Do not infer that GitHub is read-only merely because write actions are not present in the initial tool list or because direct local `git`/shell access is unavailable.** Fresh/temporary ChatGPT sessions may expose only a subset of connector actions until the relevant GitHub write capability is discovered/loaded.

Before reporting any blocker such as `GitHub write access disabled`, `cannot commit`, `read-only session`, or `direct Git unavailable`, the worker MUST:

1. discover/load the connected GitHub actions needed for repository writes, especially file create/update operations (for example `create_file` and `update_file`, or equivalent commit/ref actions exposed by the connector);
2. use repository-native reads to obtain the current file/blob SHA when an update/takeover requires optimistic concurrency;
3. attempt the actual protocol-required write — normally the atomic claim creation or takeover — rather than creating an unrelated test file;
4. only declare a write blocker if write-action discovery genuinely exposes no usable write operation, or an actual required write invocation returns an authentication/authorization/connector error.

If one required write is rejected by a tool, policy, safety, transport, connector, or stale-SHA layer, do not bypass that layer and do not end the worker merely because of that rejection. Refetch live state/SHA, retry through a normal supported repository operation when appropriate, or switch immediately to another protocol-valid eligible unit/path and continue useful work. One or two rejected writes are not a voluntary handoff reason before the normal handoff boundary.

If a required write fails, the worker must try other repository paths that can safely perform the next step before ending. A failure of one backend, local shell, container, network path, or connector operation is not by itself a task-level blocker.

Do not substitute public-web GitHub reads for the connected GitHub connector when repository writes are required. Do not abandon claimable work solely because local `git` is unavailable.

### Mode A: translation audit

If `translation_review_gate.enabled == true` or `claims_allowed == false`:

- use `TRANSLATION_REVIEW.md`;
- read `work/translation_review/active_plan.json`;
- claim/resume exactly one translation-review batch at a time;
- do not inspect UI/new-translation work while this gate remains active.

**Important:** in this state, `claims_allowed: false` pauses **normal translation claims only**. It does **not** prohibit translation-review claims. When the translation-review gate is active, a worker with repository write capability is expected to claim/resume translation-review work.

After a batch completes, re-read only the live state needed to confirm the gate/priority and immediately claim/resume the next eligible review batch if still before the configured new-work cutoff.

### Mode B: UI audit

Only after the translation-review gate clears:

- read `work/ui_review/active_plan.json`;
- if active assignable UI work remains, use `UI_REVIEW.md` and claim/resume one UI batch at a time;
- do not start new translation while required UI audit remains assignable.

After a UI batch completes, re-read live priority and continue another eligible UI batch while before the cutoff.

### Mode C: new translation

Only when translation audit is clear and no higher-priority required UI audit remains:

- use `PARALLEL_TRANSLATION.md`;
- load current epoch metadata;
- claim/resume one pinned source shard at a time.

After a shard completes, re-evaluate priority from live state and claim/resume another eligible shard while before the cutoff.

## Session budget

Use `work/worker_session_policy.json` as canonical timing policy.

The current policy defines four distinct concepts:

- `session_minutes`: hard outer budget;
- `productive_target_minutes`: minimum voluntary useful-work target;
- `stop_new_batch_after_minutes`: latest point to start another unit;
- `handoff_start_minutes`: point to begin clean final checkpoint/release.

Expected cadence:

- first minute: state + mode + claim/resume;
- main session: continuous useful review/translation work;
- checkpoint every configured item count or heartbeat interval;
- **checkpoint and continue** — checkpointing is not a stop condition;
- if a unit completes before `stop_new_batch_after_minutes`, immediately claim/resume another eligible unit;
- at `handoff_start_minutes`, stop broad new work and save/release cleanly;
- hard stop within `session_minutes`.

Do not voluntarily hand off before `productive_target_minutes` while any protocol-valid useful work remains. There is no worker-defined early-stop exception. If the current unit/path cannot progress, immediately switch to the next safe eligible unit/path at the same priority. A checkpoint, completed unit, competing owned claim, branch divergence, or one failed write/backend does not end the session.

Do not spend startup time bulk-reading glossary/context files.
Do not spend final handoff minutes on optional research or refactors.

## Rolling lease and immediate handoff

The shared session policy overrides longer legacy lease values for ChatGPT workers.

A claim can be:

- `active` — owned and not expired;
- `released` — immediately takeover-eligible;
- `complete` — work completed; completion marker remains authoritative.

A successor may take over a `released` claim immediately using optimistic concurrency and the current claim blob SHA. It does not wait for the old expiry timestamp.

For expired claims, use the same optimistic takeover rule.

Never overwrite another non-expired active claim.

## Partial work is durable work

Checkpoint to repository state, never only to chat.

For translation/UI review, partial result files may contain only completed decisions and have `status: "partial"` plus `completed_count`. They do not get completion markers.

A partial result exists so the current worker can safely continue and so a later worker can recover after handoff. **Its existence is not a reason for the current worker to stop.**

At actual handoff, the outgoing claim stores `partial_result_path` and completed count. The successor validates fingerprints, carries forward valid decisions into its own result, and resumes at the first unfinished item.

For normal translation, the task result path is stable across workers, so the successor validates existing saved entries and resumes from the first missing entry.

Always save the partial result **before** refreshing/releasing the claim, then continue unless the handoff condition has actually been reached.

## Throughput rules

- Prefer resumable partial work over untouched work of similar priority.
- Process batch items sequentially to make resume position obvious.
- Use embedded batch context first.
- Fetch extra glossary/game/speech/UI context only for the exact item that requires it.
- Low-confidence ambiguity should usually `defer` rather than consume a large share of a 25-minute session.
- If a batch completes before the cutoff, immediately re-read live state and claim another unit.
- Never pre-claim future work.
- Never idle after a completed batch while eligible same-priority work remains.
- A completed unit is a continuation trigger, not a session-end trigger.
- Checkpointing is not a stop condition.

## Quality is not traded for throughput

Historical error memory remains mandatory.

When relevant, use:

- `glossary/translation_regressions.generated.json`
- player-facing/community terminology
- source-bridge rules/risks
- canonical Skill names
- character registry
- structural/numeric QA

Do not reproduce any relevant `rejected_targets`.
Do not work around persistent quality guards.
Do not trust zh-CN blindly when source-bridge risk says it is lossy.

## Ownership

Workers never directly edit canonical output/progress state unless their selected protocol explicitly assigns that write.

In review modes, workers write only their own claim/result/completion and own heartbeat/release state. Merge workflows apply accepted changes.

In normal translation mode, workers write only isolated task claim/result/completion files. Aggregation applies accepted translations.

## End of session

Finishing the current unit does not automatically end the session.

If current work completes before `stop_new_batch_after_minutes`:

1. save final result/completion marker for that unit;
2. re-read live routing state;
3. claim/resume the next eligible unit at the same highest priority;
4. continue until the cutoff/handoff condition.

At actual handoff, if the current unit is incomplete:

1. save latest valid partial state;
2. mark only your own claim `released`;
3. include `released_at`, `partial_result_path`, and completed/translated count;
4. commit/push;
5. stop.

End report should be short: mode, all batch/task IDs handled in the run, aggregate completed counts, partial handoff if any, claim status, blockers, and final live gate/state.

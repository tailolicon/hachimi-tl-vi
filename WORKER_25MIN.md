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

## Mandatory GitHub write-capability discovery

This worker system is repository-coordinated. Claim, checkpoint, completion, heartbeat, and handoff state must be written to `main` through the connected GitHub capability available in the current session.

**Do not infer that GitHub is read-only merely because write actions are not present in the initial tool list or because direct local `git`/shell access is unavailable.** Fresh/temporary ChatGPT sessions may expose only a subset of connector actions until the relevant GitHub write capability is discovered/loaded.

Before reporting any blocker such as `GitHub write access disabled`, `cannot commit`, `read-only session`, or `direct Git unavailable`, the worker MUST:

1. discover/load the connected GitHub actions needed for repository writes, especially file create/update operations (for example `create_file` and `update_file`, or equivalent commit/ref actions exposed by the connector);
2. use repository-native reads to obtain the current file/blob SHA when an update/takeover requires optimistic concurrency;
3. attempt the actual protocol-required write — normally the atomic claim creation or takeover — rather than creating an unrelated test file;
4. only declare a write blocker if write-action discovery genuinely exposes no usable write operation, or an actual required write invocation returns an authentication/authorization/connector error.

If a required write fails, the end report must include the concrete failed operation and the actual error category/message. Absence of a preloaded write tool is **not** evidence of missing permission.

Do not substitute public-web GitHub reads for the connected GitHub connector when repository writes are required. Do not abandon claimable work solely because local `git` is unavailable.

### Mode A: translation audit

If `translation_review_gate.enabled == true` or `claims_allowed == false`:

- use `TRANSLATION_REVIEW.md`;
- read `work/translation_review/active_plan.json`;
- claim/resume exactly one translation-review batch;
- do not inspect UI/new-translation work.

**Important:** in this state, `claims_allowed: false` pauses **normal translation claims only**. It does **not** prohibit translation-review claims. When the translation-review gate is active, a worker with repository write capability is expected to claim/resume translation-review work.

### Mode B: UI audit

Only after the translation-review gate clears:

- read `work/ui_review/active_plan.json`;
- if active assignable UI work remains, use `UI_REVIEW.md` and claim/resume one UI batch;
- do not start new translation while required UI audit remains assignable.

### Mode C: new translation

Only when translation audit is clear and no higher-priority required UI audit remains:

- use `PARALLEL_TRANSLATION.md`;
- load current epoch metadata;
- claim/resume one pinned source shard.

Re-evaluate this priority from live state after each completed unit.

## Session budget

Use `work/worker_session_policy.json` as canonical timing policy.

Current intended cadence:

- first minute: state + mode + claim/resume;
- main session: useful review/translation work;
- checkpoint every configured item count or heartbeat interval;
- no new batch/task after configured stop-new-work minute;
- begin clean handoff at configured handoff minute;
- hard stop at 25 minutes.

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

At handoff, the outgoing claim stores `partial_result_path` and completed count. The successor validates fingerprints, carries forward valid decisions into its own result, and resumes at the first unfinished item.

For normal translation, the task result path is stable across workers, so the successor validates existing saved entries and resumes from the first missing entry.

Always save the partial result **before** refreshing/releasing the claim.

## Throughput rules

- Prefer resumable partial work over untouched work of similar priority.
- Process batch items sequentially to make resume position obvious.
- Use embedded batch context first.
- Fetch extra glossary/game/speech/UI context only for the exact item that requires it.
- Low-confidence ambiguity should usually `defer` rather than consume a large share of a 25-minute session.
- If a batch completes early enough, immediately re-read live state and claim another unit.
- Never pre-claim future work.

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

If current work is complete, save final result and completion marker.

If incomplete:

1. save latest valid partial state;
2. mark only your own claim `released`;
3. include `released_at`, `partial_result_path`, and completed/translated count;
4. commit/push;
5. stop.

End report should be short: mode, batch/task IDs, completed counts, partial handoff if any, claim status, blockers, and final live gate/state.

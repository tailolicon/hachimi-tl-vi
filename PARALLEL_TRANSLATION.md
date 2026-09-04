# Parallel translation worker protocol

This is the canonical protocol for translating untranslated source shards after retrospective review gates allow new translation work.

It is optimized for stateless continuously running workers with rolling orphan-recovery leases, crash-safe checkpoints, and immediate platform-triggered handoff.

Repository state on `main` overrides chat history, private memory, and model priors.

## Priority gate

Always read `work/parallel_state.json` first.

If `claims_allowed == false`:

- do not create or take over normal translation claims;
- do not translate an unclaimed shard;
- switch immediately to the mode selected by `WORKER_CONTINUOUS.md`.

An active retrospective review gate does **not** by itself block translation when `claims_allowed == true`. In that dual-lane state, this protocol is valid only for workers routed here after the configured review-worker cap is already occupied. Orchestration may still prioritize unfinished UI audit after the translation-review gate clears.

## Continuous runtime policy

Read the shared file referenced by `work/parallel_state.json.worker_session_policy`.

For ChatGPT workers, its rolling lease overrides any longer legacy lease in epoch metadata. Use the shorter effective lease.

Required behavior:

- checkpoint after every configured number of translated entries and after meaningful bounded progress;
- save result first, then refresh the claim only after new durable progress;
- continuously acquire/resume the next eligible task while useful work remains and the runtime permits execution;
- only a real platform/runtime termination signal starts handoff;
- on that signal, save partial work, commit/push immediately, and mark only your own claim `released` with a pointer to the result.

## Fast startup

Read only:

1. `work/parallel_state.json`
2. `work/worker_session_policy.json`
3. current epoch metadata referenced by `current_epoch_metadata`
4. this protocol only if not already supplied/current
5. exactly one pinned source batch for the selected task
6. only the relevant glossary/regression records for that shard

Do not bulk-read all glossary, character, speech, or regression files.

## Immutable source epoch

Workers never translate from moving `source-zhcn` directly.

Use the exact `source_queue_git_commit` pinned in epoch metadata and fetch:

`work/source_batches/batch-{batch:05d}.json`

A source batch normally contains 80 entries. A parallel task is a 20-entry shard (`s00`..`s03`).

Task-local roots are defined by epoch metadata:

- claims
- results
- completed
- aggregated

Workers never write `localized_data/**` directly.

## Choosing work

After confirming the gate is open:

1. use `first_parallel_batch..queue_total_batches`;
2. skip `legacy_completed_batches`;
3. hash the unique worker id to spread workers across candidate batches/shards;
4. skip any task with authoritative completion/aggregation markers;
5. inspect claims only for candidate tasks;
6. prefer released/expired tasks with useful partial results over untouched tasks of similar priority;
7. fetch the exact pinned source batch only after choosing a candidate.

## Atomic claim and takeover

Claim file schema includes at least:

```json
{
  "schema_version": 1,
  "epoch": "zhcn-...",
  "task_id": "batch-00002-s00",
  "batch": 2,
  "shard": 0,
  "worker_id": "sol-<unique>",
  "source_commit": "...",
  "source_queue_git_commit": "...",
  "claimed_at": "UTC ISO-8601",
  "heartbeat_at": "UTC ISO-8601",
  "lease_expires_at": "UTC ISO-8601",
  "status": "active"
}
```

Fresh claim creation is the lock. If creation races, choose another task.

If a claim exists:

- authoritative completion marker => task done;
- non-expired `active` => busy;
- `released` => immediately takeover-eligible;
- expired => takeover-eligible.

Takeover uses the current claim blob SHA for optimistic concurrency. Preserve/fetch `partial_result_path` before replacing a released claim. If update conflicts, another worker won.

## Partial result and resume

The normal translation result file is already task-stable rather than claim-scoped:

`work/parallel/<epoch>/results/<group>/<task-id>.json`

This makes handoff cheap.

Partial schema includes `status: "partial"`, `translated_count`, and completed entries.

A successor must:

1. load the existing result if present;
2. verify each saved entry against the pinned batch UID/source fingerprint/index;
3. preserve valid reviewed targets;
4. discard invalid/stale/unassigned entries;
5. resume from the first missing entry instead of translating saved work again.

Never replace valid saved target text unless deliberately correcting it before completion.

## Checkpoint loop

Save after every epoch `checkpoint_every_entries` or shared heartbeat interval, whichever comes first.

Ordering is mandatory:

1. write/update the partial result;
2. only after it is durable, refresh your own claim heartbeat and effective rolling lease;
3. continue translating.

This guarantees that a worker crash after a heartbeat cannot hide unpersisted translation work.

## Context and regression lookup

Before translating the shard, load only matching/relevant records for its UIDs/source strings from:

- `glossary/translation_regressions.generated.json`
- `glossary/ui_community_terms.json`
- `glossary/source_bridge_terms.json`
- `glossary/source_bridge_risks.generated.json`
- `glossary/term_registry.json`
- `glossary/characters.json`
- `glossary/skill_name_style.json`

Use speech context only when a specific dialogue item actually requires it.

## Persistent error memory

`translation_regressions.generated.json` contains accepted corrections from retrospective translation review and UI review.

For matching identity:

- never output any `rejected_targets`;
- use the newest `approved_target` as strong reviewed guidance when context remains compatible;
- if `origins` contains `ui_review`, inspect `ui_contexts` (`key`, `control_type`, `risk_flags`) so future translations do not recreate wording rejected for real UI fit;
- higher-priority current canonical/player-facing/source-bridge policy may supersede older approved wording.

The merge firewall is authoritative. Do not work around `known_bad_regression` or deterministic QA failures.

## Source-bridge safety

zh-CN is a semantic bridge, not canonical truth.

Examples of mandatory anti-calque rules when matched:

- `金币` => approved `Monies`, not `xu`/literal gold-money wording;
- `蹄铁` => approved `Cleat/Cleats`, not `móng ngựa`.

If an exact source is marked untrusted/lossy, use JP/canonical evidence. If unresolved, do not invent a canonical translation.

## Terminology precedence

When applicable:

1. current player-facing/community terminology;
2. exact canonical individual-Skill mapping;
3. source-bridge/canonical correction;
4. reviewed regression/context memory;
5. locked registry term not overridden above;
6. established official English/Romanized Uma Musume terminology;
7. natural Vietnamese for genuinely generic concepts.

Common approved game-facing labels such as `Trainer`, `Speed`, `Stamina`, `Power`, `Guts`, `Wit`, `Skill`, `Unique Skill`, `Evolution Skill`, `Turf`, `Dirt`, `Sprint`, `Mile`, `Medium`, `Long` stay in approved forms when matched.

Verified character names use canonical Roman-letter names. Never semantically translate the Chinese name.

### Vietnamese editorial quality floor

Correct meaning is necessary but not sufficient. Player-facing Vietnamese must read like edited Vietnamese, not a clause-by-clause trace of zh-CN syntax.

- Generic `ウマ娘` / `赛马娘` / the matching world/species concept is **Mã Nương** in Vietnamese prose/dialogue. Do not treat `Mã Nương` itself as a regression; only a more-specific scoped canonical rule may override it for a particular compound or proper name.
- Preserve meaning, speaker attitude, register, emphasis, ambiguity, formatting, placeholders, and gameplay terminology, but freely reorder clauses and recast sentence structure when Vietnamese needs it.
- Prefer concise idiomatic Vietnamese over constructions that mirror Chinese word order. Avoid awkward patterns such as topic fragments followed by a second subject (`Tôi, chúng tôi...`) or nominalized calques such as `tính đúng đắn trong những gì...` when a natural finite clause expresses the same meaning.
- Dialogue must sound speakable. UI/help text must sound like native game copy. Do not add information, intensify emotion, flatten characterization, or paraphrase away meaningful nuance just to sound smoother.
- Before marking an entry reviewed, perform one Vietnamese-only reread: if the target sounds translated when read without the source beside it, rewrite it while preserving the source meaning and all locked terms.

## Semantic QA

For every entry preserve/check:

- subject/object;
- polarity and negation;
- can/cannot, already/not-yet, presence/absence;
- conditions;
- upper/lower bounds and comparisons;
- increase/decrease direction;
- all numeric tokens/values;
- mechanic relationships and implications;
- no unsupported addition or omission.

Fluent Vietnamese with changed mechanics is wrong.

## Structural QA

Preserve exactly:

- placeholders (`{0}`, `{1}`, `{name}`...);
- printf/runtime/template tokens;
- markup tags;
- escaped sequences;
- IDs/URLs when applicable;
- intended newline structure;
- numeric values.

## Required review passes

Before marking an entry reviewed:

1. semantic translation;
2. Vietnamese fluency/terminology;
3. regression/source-bridge review;
4. placeholder/markup/newline/numeric QA.

## Completing a task

A task is complete only when every source entry in the shard has one reviewed target and structural + persistent QA passes.

1. save result with `status: "complete"` and full shard entries;
2. create completion marker with exact task/result/source metadata, `entry_count` equal to the exact shard entry count, and `qa_passed: true`;
3. optionally mark your claim `status: "complete"`;
4. re-read live gate/state before acquiring more work.

For a normal 20-entry shard, the completion marker must therefore include at least:

```json
{
  "schema_version": 1,
  "epoch": "zhcn-...",
  "task_id": "batch-00002-s00",
  "batch": 2,
  "shard": 0,
  "source_commit": "...",
  "source_queue_git_commit": "...",
  "result_path": "work/parallel/<epoch>/results/<group>/batch-00002-s00.json",
  "entry_count": 20,
  "qa_passed": true,
  "completed_at": "UTC ISO-8601",
  "worker_id": "sol-<unique>"
}
```

`translated_count` may remain on older markers or be included as redundant metadata, but new completion markers must write `entry_count`. The aggregator accepts the historical `translated_count` alias so already-durable valid work is not stranded. If both count fields are present, they must agree.

Completion marker is authoritative.

## Session-end handoff

At `handoff_start_minutes`, stop optional research and new task acquisition.

If current task is incomplete:

1. save latest partial result;
2. update only your own claim to `status: "released"`;
3. include `released_at`, `partial_result_path`, and `translated_count`;
4. commit/push the release;
5. stop.

A successor may atomically take over the released claim immediately and continue from the stable task result. It does not wait for the old lease expiry.

## Aggregation

`.github/workflows/aggregate-results.yml` independently validates completed task results against the pinned source batch and persistent quality guard, applies valid work to `localized_data/`, rebuilds `index.json`, and publishes release output.

Workers never merge their own translation directly.

## Learning from review

Accepted translation-review and UI-review `revise` decisions are automatically mined into unified regression memory. `keep`, unresolved `defer`, low-confidence, and auto-deferred proposals are not promoted as hard rejected targets.

## Continuous loop

After completion:

1. re-read `work/parallel_state.json`;
2. if the retrospective gate re-closes, switch to the protocol selected by `WORKER_CONTINUOUS.md`;
3. otherwise claim/resume another available shard and continue while useful work remains and the runtime permits execution.

Do not end because of elapsed time. Only an actual platform/runtime termination signal starts emergency handoff, and that handoff prioritizes immediate durable commit/push/release.

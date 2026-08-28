# Parallel translation review workers

This is the canonical retrospective QA protocol for translations already merged into Vietnamese.

The system is optimized for stateless ChatGPT workers with a hard 25-minute session. The goals are: minimal startup context, maximum reviewed entries per session, crash-safe checkpoints, and immediate handoff to another worker.

Repository state on `main` overrides chat history, private memory, and model priors. Current Vietnamese text is a hypothesis, not evidence that it is correct.

## Gate and priority

`work/parallel_state.json.translation_review_gate` is authoritative.

While `enabled: true` or `claims_allowed: false`:

- do not create or take over normal translation claims;
- review already merged translations only;
- `defer` remains unresolved and keeps the gate closed.

The gate clears only when every canonical entry in review scope has a current resolved `keep` or `revise` decision.

## 25-minute worker policy

Read `work/worker_session_policy.json` and obey it even when an old plan advertises a longer lease.

For ChatGPT workers, the effective rolling lease is the shorter of the plan lease and `rolling_lease_minutes` in the shared session policy.

Current session discipline is intentionally throughput-first:

- checkpoint every 5 completed decisions or every heartbeat interval, whichever comes first;
- save the result checkpoint **before** refreshing the claim;
- refresh only after the checkpoint is durable on `main`;
- do not claim a new batch after `stop_new_batch_after_minutes`;
- begin handoff by `handoff_start_minutes`;
- never intentionally leave an active claim when the 25-minute session ends.

A normal clean session should finish one or more 20-entry batches. If it cannot finish the current batch, it must leave a resumable partial result rather than lose completed decisions.

## Fast startup

Read only:

1. `work/parallel_state.json`
2. the file referenced by `worker_session_policy`
3. `work/translation_review/active_plan.json`
4. this protocol only if its version/content has not already been supplied to the worker
5. exactly one selected batch file

Do **not** read the full plan file by default.
Do **not** pre-read `GAME_CONTEXT.md`, full glossary files, character registries, or speech files.

The normal hot path is therefore three tiny control files plus one 20-entry batch.

## Choosing work without reading the full plan

`active_plan.json` provides `plan_id`, `batch_count`, and normally `priority_batch_ids`.

1. Try `priority_batch_ids` first.
2. A batch is unavailable if `work/translation_review/merged/<batch_id>.json` exists.
3. Inspect `work/translation_review/claims/<batch_id>.json` only for candidate batches.
4. A non-expired `active` claim is busy.
5. A `released` claim is immediately takeover-eligible even if its old expiry time has not passed.
6. An expired claim is takeover-eligible.
7. If the priority head is busy, hash the unique worker id into `1..batch_count`, then probe cyclically.
8. Batch paths are deterministic: `work/translation_review/batches/<plan_id>/<plan_id>-bNNNN.json`.

Prefer a released/expired batch with saved partial work over an untouched batch of similar priority because finishing existing work yields faster completed throughput.

There is no need to load `work/translation_review/plans/<plan_id>.json` during normal work.

## Atomic claim and takeover

Claim path:

`work/translation_review/claims/<batch_id>.json`

A fresh claim contains at least:

```json
{
  "schema_version": 1,
  "plan_id": "...",
  "batch_id": "...",
  "claim_id": "trc-<unique>",
  "worker_id": "<unique worker>",
  "status": "active",
  "claimed_at": "UTC ISO-8601",
  "heartbeat_at": "UTC ISO-8601",
  "expires_at": "UTC ISO-8601"
}
```

Create the file atomically. If another worker wins the create race, choose another batch.

For a released or expired claim, fetch its current blob SHA and replace it atomically with a new `claim_id`, worker id, timestamps, `status: "active"`, and a fresh rolling lease. If the update conflicts, another worker won the takeover.

When taking over a released claim, preserve the old `partial_result_path` long enough to fetch the handoff result before replacing the claim. For an expired claim without a pointer, inspect `work/translation_review/results/<batch_id>/` for the newest partial result that matches the current `plan_id` and batch fingerprints.

Never overwrite another non-expired active claim.

## Resuming partial work

Partial checkpoints are first-class handoff state.

A partial result uses the normal claim-scoped result path:

`work/translation_review/results/<batch_id>/<claim_id>.json`

and may contain only the decisions completed so far:

```json
{
  "schema_version": 1,
  "status": "partial",
  "plan_id": "...",
  "batch_id": "...",
  "claim_id": "...",
  "worker_id": "...",
  "reviewed_at": "...",
  "completed_count": 5,
  "decisions": []
}
```

A partial result has **no completion marker** and therefore cannot be merged.

A successor must:

1. load the current batch;
2. load the handed-off partial result;
3. copy only decisions whose UID belongs to the batch and whose `current_fingerprint` still matches exactly;
4. discard duplicate/stale/unassigned decisions;
5. write the carried decisions into its own new claim-scoped result;
6. continue from the first unfinished UID instead of re-reviewing valid carried decisions.

The final result under the successor's claim must contain all and only batch UIDs exactly once.

## Embedded-first context

Each translation-review batch already contains source/current text, fingerprints, source path, structural identity, risk flags, and where applicable:

- `locked_terms`
- `community_terms`
- `skill_name_canonical`
- `source_bridge_terms`
- `source_bridge_risks`

Use embedded data first. Do not reopen a full registry just to reconfirm information already embedded in the batch.

## Lazy extra context

Fetch extra repository context only for an item that cannot be safely judged from its batch data.

For an unresolved mechanic/term, search the exact source/name in only the relevant records of:

- `glossary/ui_community_terms.json`
- `glossary/term_registry.json`
- `glossary/skill_name_style.json`
- `glossary/translation_regressions.generated.json`
- `GAME_CONTEXT.md`

For uncertain proper names, search the exact alias in `glossary/characters.json`.

For attributable dialogue where voice genuinely changes the decision, search only the relevant speaker/relationship records in speech files. Do not load all speech context for UI/system/skill text.

If evidence is still weak, `defer`; do not spend a large part of a 25-minute session inventing a canonical answer.

## Review gates

For every item check:

1. meaning: subject/object, polarity, conditions, comparison, quantity, direction, omission/addition;
2. natural Vietnamese;
3. canonical/player-facing terminology;
4. source-bridge safety for zh-CN;
5. proper-name/Skill identity when applicable;
6. historical regression memory when relevant;
7. structure: placeholders, printf tokens, tags, runtime tokens, numeric values, and newline structure.

Translation review may repair semantic/naturalness problems in UI text. Fixed-control clipping/compactness is handled by `UI_REVIEW.md`.

## Decisions

Every assigned UID eventually receives exactly one action:

- `keep` — current text passes all applicable gates;
- `revise` — confident correction;
- `defer` — evidence insufficient; remains unresolved.

Low-confidence correction means `defer`, never guess.

For `keep`/`revise`, if the item has `locked_terms`, `community_terms`, or `skill_name_canonical`, include non-empty `terminology_basis`.

## Checkpoint loop

Work sequentially through the batch.

After every `checkpoint_every_decisions` newly completed decisions, or when the heartbeat interval is reached:

1. write/update your claim-scoped result with `status: "partial"`, `completed_count`, and all valid decisions completed so far;
2. only after that write succeeds, update your own claim heartbeat and rolling `expires_at`;
3. continue from the next unfinished UID.

Do not checkpoint only in chat. Repository state is the handoff state.

## Final result

When all assigned UIDs are decided, write:

```json
{
  "schema_version": 1,
  "status": "complete",
  "plan_id": "...",
  "batch_id": "...",
  "claim_id": "...",
  "worker_id": "...",
  "reviewed_at": "...",
  "completed_count": 20,
  "decisions": [
    {
      "uid": "zhcn:...",
      "current_fingerprint": "...",
      "action": "keep|revise|defer",
      "proposed_text": "only for revise",
      "reason": "...",
      "terminology_basis": "when applicable",
      "speech_basis": "when applicable",
      "confidence": "high|medium|low"
    }
  ]
}
```

Extra `status`/`completed_count` fields are worker metadata; merge authority still comes only from a completion marker.

## Completion

Only after the complete result is durable, create:

`work/translation_review/completions/<batch_id>/<claim_id>.json`

with exact `plan_id`, `batch_id`, `claim_id`, `worker_id`, result path, and UTC `completed_at`.

Then mark your own claim `status: "complete"` if useful. The completion marker is authoritative.

The merge workflow independently validates fingerprint freshness, terminology, Skill-title constraints, source-bridge rules, and structural QA.

## Session-end handoff

At `handoff_start_minutes`, stop optional research and new work acquisition.

If the batch is complete, finish result + completion normally.

If incomplete:

1. save the latest valid partial result;
2. update only your own claim to:

```json
{
  "status": "released",
  "released_at": "UTC ISO-8601",
  "partial_result_path": "work/translation_review/results/<batch_id>/<claim_id>.json",
  "completed_count": 15
}
```

while preserving the identifying plan/batch/claim/worker fields and current timestamps;
3. commit/push the release;
4. stop.

A `released` claim is immediately available for optimistic takeover. Do not wait for its old lease expiry.

## Ownership

Review workers edit only their own claim/result/completion and their own claim heartbeat/release state.

Never directly edit:

- `localized_data/**`
- `work/merged/**`
- `work/translation_progress.json`
- `work/parallel_state.json`
- `work/translation_review/reviewed_index.json`
- canonical glossary/speech files

## Continuous loop

After a completed batch:

1. re-read only `work/parallel_state.json` and `work/translation_review/active_plan.json`;
2. if the plan changed, use the new plan id;
3. if session elapsed time is before `stop_new_batch_after_minutes`, claim another available/resumable batch;
4. otherwise end cleanly without acquiring more work.

Do not reread this protocol unless it changed.

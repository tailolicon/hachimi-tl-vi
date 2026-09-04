# Parallel translation review workers

This is the canonical retrospective QA protocol for translations already merged into Vietnamese.

The system is optimized for stateless continuously running workers. The goals are: minimal startup context, high review throughput, crash-safe checkpoints, and immediate platform-triggered durable handoff.

Repository state on `main` overrides chat history, private memory, and model priors. Current Vietnamese text is a hypothesis, not evidence that it is correct.

## Gate and priority

`work/parallel_state.json.translation_review_gate` is authoritative.

While `enabled: true`, retrospective review remains required and `defer` remains unresolved.

`claims_allowed` controls the separate new-translation lane:

- `claims_allowed: false` means review is exclusive/fail-closed;
- `claims_allowed: true` means review and new translation run concurrently; `WORKER_CONTINUOUS.md` keeps up to `review_worker_cap` live review workers and routes excess workers to translation.

The review gate itself clears only when every canonical entry in its frozen review scope has a current resolved `keep` or `revise` decision. Clearing the audit gate is no longer required merely to increase pinned-source coverage.

## Continuous runtime policy

Read `work/worker_session_policy.json` and obey it even when an old plan advertises a longer lease.

For ChatGPT workers, the effective rolling lease is the shorter of the plan lease and `rolling_lease_minutes` in the shared session policy.

Runtime discipline is intentionally throughput-first:

- checkpoint every 5 completed decisions and after meaningful bounded progress;
- save the result checkpoint **before** refreshing the claim;
- refresh only after the checkpoint is durable on `main`;
- after a completed batch, immediately re-read live routing and claim/resume the next eligible batch while useful work remains;
- do not self-time or voluntarily stop because of elapsed time;
- only a real platform/runtime termination signal starts handoff, and then the worker must save, commit/push, and release as quickly as possible.

If the platform interrupts an incomplete batch, leave a resumable partial result rather than lose completed decisions.

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
- `canonical_findings` — open systemic findings that block matching entries until canonical context is resolved

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

If evidence is still weak, `defer`; do not spend disproportionate effort inventing a canonical answer.

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

## Canonical-first discovery

If an item reveals a reusable/systemic terminology, proper-name, source-bridge, context-rule, or system-label problem that is not already safely canonicalized, do not establish a one-off translation and move on. Attach a `canonical_finding` to the decision and normally `defer` the item until canonical maintenance resolves it.

```json
"canonical_finding": {
  "kind": "terminology|proper_name|source_bridge|context_rule|system_label",
  "source_zh_cn": "相性",
  "suggested_target_vi": "Affinity",
  "concept": "Legacy Affinity",
  "match_mode": "contains",
  "scope": "source_path",
  "reason": "Repeated player-facing concept needs one canonical label.",
  "confidence": "high"
}
```

Use the smallest alias that actually identifies the concept. Default to exact matching; use `contains` only for a clearly reusable concept. Prefer `scope=auto`; broaden to `source_path` only with strong evidence. Omit `suggested_target_vi` rather than guess. Isolated naturalness fixes are not canonical findings.

The merge pipeline deduplicates findings into `glossary/canonical_findings.json`. That ledger is evidence, not canonical. Open findings are item-scoped blocking context, are pushed near the top of the terminology-review queue, and normalize matching `keep`/`revise` decisions to `defer`. When matching canonical context lands, resolution refresh unblocks the finding and affected entries reopen under the new canonical context. Explicit `ignore` unblocks; explicit `defer` remains blocking.


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
      "canonical_finding": "optional systemic finding object",
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
- `glossary/canonical_findings.json` directly (findings travel through the worker result and merge centrally)

## Continuous loop

After a completed batch:

1. re-read only `work/parallel_state.json` and `work/translation_review/active_plan.json`;
2. if the plan changed, use the new plan id;
3. claim/resume another available batch while useful work remains and the runtime permits execution.

Do not reread this protocol unless it changed. Do not end because of elapsed time; only an actual platform/runtime termination signal starts emergency save/commit/push/release.

## Manual-audit canonical rules

`glossary/translation_audit_policy.json` defines the explicit full-corpus audit round. It is part of the global review context hash. Incrementing `audit_round` intentionally reopens every currently merged translation, even if all other glossary files are unchanged. A cleared gate means only that the **current audit round** is clean; it is not a permanent assertion that future audits can find nothing else.

Apply these project-owner audit decisions as hard review policy:

- generic `ウマ娘` / `赛马娘` in world/prose/dialogue is **Mã Nương**; preserve the product/franchise title **Umamusume: Pretty Derby** when the full title is present;
- established gameplay vocabulary stays player-facing: **Support Card, Mood, Speed, Stamina, Power, Guts, Wit, Skill, Skill Pt/Skill Points, Skill Hint, Spark/Sparks, Turf, Dirt, Sprint, Mile, Medium, Long, Front Runner, Pace Chaser, Late Surger, End Closer, Runaway**;
- named Conditions use their established English names (for example `夜ふかし気味` / quoted `熬夜` condition → **Night Owl**). Do not replace ordinary prose containing similar words with a Condition name;
- individual Skill names still follow the Vietnamese Skill-title style/canonical registry; the keep-English rule above applies to generic gameplay labels, not every Skill title;
- song titles and race names are proper names: use the verified international/official Romanized or English form, never a literal zh-CN semantic calque. If the international form is not established in repository evidence, verify it or `defer`;
- song/person credits must use a verified Latin/Roman spelling for real creator names. CJK creator names left verbatim are not considered a clean Vietnamese result merely because the credit label was translated;
- zh-CN-only translator/editor credits such as `译：...` are bridge metadata, not automatically original game credits. If the corresponding JP source/official credit cannot confirm them, remove them when evidence is clear or `defer` instead of propagating the bridge artifact;
- `text_data` category `171` is interaction/login trigger metadata. Translate it as a condition/trigger label (for example “Khi đăng nhập buổi sáng”) rather than mistaking it for normal dialogue or an imperative UI action;
- `text_data` category `172` is inheritance/Spark description context. Literal `因子 → Nhân tố`, `技能Pt → điểm/Pt kỹ năng`, or `技能灵感 → Gợi ý Skill` is noncanonical;
- a terminology rule discovered by manual audit must be fixed in canonical context first. Do not patch only the sampled line and leave the same wrong mapping reusable elsewhere.

After the game reaches full translation, start additional whole-corpus audit rounds by incrementing `audit_round`. Multiple clean passes are expected because later context, newly translated content, and manual sampling can expose systemic errors that an earlier pass could not see.


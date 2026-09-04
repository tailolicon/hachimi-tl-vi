# Parallel UI review workers

This is the canonical retrospective UI-quality protocol for already translated fixed-size UI text in `localized_data/localize_dict.json`.

It is optimized for stateless continuously running workers: minimal startup reads, 20-entry batches, frequent durable checkpoints, and immediate platform-triggered released-claim handoff.

Repository state on `main` overrides chat history, private memory, and model priors. Current Vietnamese is a hypothesis, not proof that it is correct.

## Purpose

UI review has two independent gates:

1. **game-language correctness** — canonical/player-facing terminology, named mechanics, resources, event/mode names, Skill categories, individual Skill titles, proper names;
2. **visual correctness** — fit the actual control without clipping, extreme shrinking, awkward wrapping, redundant wording, bad slash compounds, or unnecessary width.

A semantically understandable string can still fail UI QA.

Do not use this pipeline for story dialogue, lyrics, long prose, or character conversation.

## Work priority

Normal orchestration must first check `work/parallel_state.json.translation_review_gate`.

If retrospective translation audit is still required, translation review has higher priority and the worker should follow `TRANSLATION_REVIEW.md` instead.

UI review becomes the next priority after the translation-review gate is cleared and the UI active plan still has assignable work.

## Continuous runtime policy

Read `work/worker_session_policy.json` through the path referenced by `work/parallel_state.json`.

For ChatGPT workers, use the shared rolling lease even if an old UI plan advertises a longer lease.

Required behavior:

- checkpoint after every 5 completed decisions and after meaningful bounded progress;
- save partial result before refreshing the claim;
- refresh the rolling lease only after new durable progress;
- continuously claim/resume another eligible batch while useful work remains and the runtime permits execution;
- only a real platform/runtime termination signal starts handoff; then save, commit/push, and release incomplete work with a pointer to the latest partial result as quickly as possible.

## Fast startup: do not bulk-read context

Normal startup reads only:

1. `work/parallel_state.json`
2. `work/worker_session_policy.json`
3. `work/ui_review/active_plan.json`
4. this protocol only if not already supplied/current
5. exactly one selected UI batch

Do **not** pre-read the full UI plan.
Do **not** pre-read all of `GAME_CONTEXT.md`, `term_registry.json`, `skill_name_style.json`, `ui_short_forms.json`, `ui_overrides.json`, `style_rules.json`, or the regression memory.

Fetch targeted extra context only for an item that actually needs it.

## Choosing a batch without reading the full plan

If `work/ui_review/active_plan.json.status != "active"`, there is no assignable UI review work.

UI batch paths are deterministic:

`work/ui_review/batches/<plan_id>/<plan_id>-bNNNN.json`

The active plan gives `plan_id` and `batch_count`. UI candidates are generated in descending risk order, so low numeric batch ids are high-priority.

To reduce collisions across many workers:

1. first probe a small high-risk window using a deterministic offset from the unique worker id;
2. then probe the full `1..batch_count` range cyclically;
3. skip `work/ui_review/merged/<batch_id>.json` if present;
4. inspect a claim only after selecting a candidate batch;
5. a non-expired `active` claim is busy;
6. a `released` claim is immediately takeover-eligible;
7. an expired claim is takeover-eligible.

Prefer resumable partial work over an untouched batch of similar priority.

There is no need to load the full plan during normal work.

## Atomic claim and takeover

Claim path:

`work/ui_review/claims/<batch_id>.json`

Fresh claim:

```json
{
  "schema_version": 1,
  "plan_id": "...",
  "batch_id": "...",
  "claim_id": "ui-<unique>",
  "worker_id": "<unique worker>",
  "status": "active",
  "claimed_at": "UTC ISO-8601",
  "heartbeat_at": "UTC ISO-8601",
  "expires_at": "UTC ISO-8601"
}
```

Create atomically. If another worker wins, choose another candidate.

For `released` or expired claims, use the current claim blob SHA to atomically replace it with your own new claim id/worker/timestamps/rolling lease. Preserve and fetch any old `partial_result_path` before replacing the claim. If the update conflicts, another worker won the takeover.

Never overwrite another non-expired active claim.

## Partial checkpoint and resume

Partial result path:

`work/ui_review/results/<batch_id>/<claim_id>.json`

A checkpoint may contain only completed keys:

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

A partial result has no completion marker and cannot be merged.

A successor taking over must copy only decisions whose `key` is assigned by the current batch and whose `current_fingerprint` still matches exactly. Write those carried decisions into the successor's own claim-scoped result, then continue from the first unfinished key.

If a released claim has no valid pointer, inspect `work/ui_review/results/<batch_id>/` for the newest matching partial result.

## Embedded-first batch context

Every UI batch already embeds:

- key/path/UID where available;
- source and current Vietnamese text;
- source/current fingerprints;
- approximate source/current visual width;
- `risk_flags` and `risk_score`;
- matched `community_terms` when recognized.

Use those fields first. Automatic risk flags are hints, not verdicts, but `community_calque_risk` and `community_term_mismatch` are high-priority warnings.

## Lazy targeted context

Only when the batch itself is insufficient, fetch exact relevant records from:

- `glossary/translation_regressions.generated.json` — first choice for known previous UI/translation mistakes;
- `glossary/ui_community_terms.json` — player-facing common mechanics/labels;
- `glossary/ui_short_forms.json` — compact/micro forms for cramped controls;
- `glossary/ui_overrides.json` — already reviewed key-specific UI wording;
- `glossary/skill_name_style.json` — individual Skill-title exact examples/style;
- `glossary/term_registry.json` — locked terms not overridden by higher-priority rules;
- `GAME_CONTEXT.md` — only for unresolved mechanic/context questions;
- `UI_TRANSLATION_RULES.md` — only when detailed width/control guidance is needed.

Search exact source/key/term; do not read whole large files end-to-end if targeted retrieval is available.

If evidence remains weak, `defer` instead of spending disproportionate effort inventing a canonical answer.

## Regression memory is mandatory when relevant

`glossary/translation_regressions.generated.json` contains accepted corrections from both translation review and UI review.

For a matching UID/source identity:

- never reuse `rejected_targets`;
- use the latest `approved_target` as strong reviewed guidance when context still matches;
- if `origins` includes `ui_review`, inspect `ui_contexts` such as key, `control_type`, and `risk_flags` because the old text may have been rejected specifically for width/control fit.

Do not recreate a longer semantically equivalent wording that UI review already rejected.

## Terminology precedence

When rules overlap:

1. player-facing/community accepted form;
2. exact canonical individual-Skill example;
3. source-bridge/canonical correction when relevant;
4. reviewed regression or key-specific UI override;
5. locked registry term not overridden above;
6. established official English/Romanized Uma Musume terminology;
7. natural Vietnamese for genuinely generic concepts.

Common labels such as `Trainer`, `Speed`, `Stamina`, `Power`, `Guts`, `Wit`, `Aptitude`, `Turf`, `Dirt`, `Sprint`, `Mile`, `Medium`, `Long`, `Style`, `Skill`, `Unique Skill`, and `Evolution Skill` stay in approved player-facing forms when matched.

Never fix width by translating an approved English/Romanized mechanic/stat/style label back into Vietnamese.

## Review decisions

For every assigned key eventually choose exactly one:

- `keep` — passes terminology/game-language QA and visual QA;
- `revise` — confident, better player-facing/compact wording;
- `defer` — context/terminology/layout evidence insufficient.

Low-confidence change means `defer`.

If `community_terms` is non-empty, `keep`/`revise` needs a non-empty `terminology_basis`.

`control_type` may be `unknown` when not safely inferable; do not guess it merely to fill a field.

## Visual QA

For fixed controls:

- semantic correctness alone is insufficient;
- prefer compact wording for buttons/tabs/menu tiles;
- remove context already obvious from the screen/icon;
- avoid unnecessary slash-separated phrases;
- do not add an extra newline to rescue width;
- preserve source newline count and runtime syntax;
- do not shorten so aggressively that the action/mechanic changes meaning;
- preserve reviewed compact forms where they exist;
- individual Skill titles follow Skill-title policy, not effect-sentence paraphrases.

A revision should normally not be wider than the current text and should fit the apparent control budget.

## Checkpoint loop

After every configured checkpoint size or heartbeat interval:

1. save/update your claim-scoped result as `status: "partial"` with all valid completed decisions;
2. only after that succeeds, refresh your own claim heartbeat and rolling lease;
3. continue from the next unfinished key.

Do not keep completed UI review work only in chat.

## Final result

When all assigned keys are reviewed, write one complete result:

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
      "key": "Heroes511003",
      "current_fingerprint": "...",
      "action": "revise",
      "proposed_text": "Chi tiết Hero Gauge",
      "control_type": "header",
      "reason": "...",
      "terminology_basis": "when applicable",
      "confidence": "high|medium|low"
    }
  ]
}
```

Before completion verify all and only batch keys appear exactly once, fingerprints match, structure/newlines/tokens are preserved, and no known forbidden/rejected wording survives a `keep`/`revise`.

## Completion

Only after the complete result is durable, create:

`work/ui_review/completions/<batch_id>/<claim_id>.json`

with exact plan/batch/claim/worker IDs, exact result path, and UTC completion time.

Then optionally mark your own claim `status: "complete"`. The completion marker is authoritative. `.github/workflows/merge-ui-review.yml` exclusively applies accepted changes and updates UI overrides/regression memory.

## Session-end handoff

At `handoff_start_minutes`, stop optional research and new batch acquisition.

If incomplete:

1. save the newest valid partial result;
2. update only your own claim to `status: "released"`;
3. add `released_at`, `partial_result_path`, and `completed_count`;
4. commit/push the release;
5. stop.

A released claim is immediately takeover-eligible; the successor does not wait for the old expiry.

## Ownership

UI review workers never directly edit:

- `localized_data/**`
- `glossary/ui_overrides.json`
- `glossary/ui_short_forms.json`
- `glossary/ui_community_terms.json`
- `glossary/skill_name_style.json`
- `glossary/term_registry.json`
- `work/ui_review/reviewed_index.json`
- translation progress/results or curation canonical files

Workers edit only their own claim/result/completion and own heartbeat/release state.

## Continuous loop

After each completed batch:

1. re-read only `work/parallel_state.json` and `work/ui_review/active_plan.json`;
2. claim/resume another available batch while useful work remains and the runtime permits execution.

Do not end because of elapsed time. Only an actual platform/runtime termination signal starts emergency handoff; save/commit/push/release first, then keep any final report minimal.

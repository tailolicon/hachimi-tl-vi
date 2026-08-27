# Parallel translation review workers

This is the canonical retrospective quality gate for **already merged Vietnamese translations**.

It is separate from speech/terminology curation and from fixed-size `UI_REVIEW.md`. Speech/terminology provide context; UI review remains the specialist visual-fit pass. Translation review decides whether the translated text itself is faithful, natural, game-correct, and structurally safe.

## Gate semantics

`work/parallel_state.json.translation_review_gate` is authoritative.

When `translation_review_gate.enabled` is `true`:

- translation workers MUST NOT create or take over new translation claims;
- existing merged translation progress is not reset or subtracted;
- workers should use this protocol instead;
- the gate remains closed while any current canonical entry is unreviewed or `defer`.

`defer` is intentionally **not** a pass. Deferred entries are re-enqueued by the next review plan and continue blocking new translation work.

The plan builder opens the gate whenever unresolved canonical translations exist and clears it only when all entries represented by `work/merged/*.json` have a current `keep` or `revise` decision under the active review policy/context.

## Scope

The review source of truth is the intersection of:

1. canonical merged markers in `work/merged/batch-*.json`;
2. the immutable source batch/ref recorded by each marker;
3. the current target text in `localized_data/**`.

This means the initial baseline reviews every canonical translation already completed. It does **not** change the translation percentage and does not count untranslated queue entries.

A completed-but-not-yet-aggregated translation is picked up by a later delta review plan after it becomes canonical.

## Mandatory context

Before claiming a batch, read from `main`:

1. `TRANSLATION_REVIEW.md`
2. `GAME_CONTEXT.md`
3. `glossary/term_registry.json`
4. `glossary/ui_community_terms.json`
5. `glossary/skill_name_style.json`
6. `glossary/style_rules.json`
7. `glossary/characters.json`
8. `glossary/speech_bible.json`
9. `glossary/speech_samples.json`
10. `glossary/speech_evidence.json`
11. `work/translation_review/active_plan.json`
12. the referenced active plan
13. the specific batch file

Repository state overrides chat history and model priors. The current Vietnamese target is a hypothesis, not evidence that its wording is correct.

## Quality gates

Review every assigned item for all of the following.

### 1. Meaning fidelity

- Preserve the actual source meaning, subject/object relation, polarity, conditions, quantities, and intent.
- Reject omissions, additions, over-explanations, and plausible-sounding rewrites that are not supported by the source.
- Names and proper nouns are identities, not opportunities for semantic calques.
- If zh-CN wording is ambiguous and repository context does not resolve it, use `defer`.

### 2. Natural Vietnamese

- The result must read like shipped Vietnamese game text, not word-by-word machine translation.
- Prefer concise, idiomatic phrasing appropriate to the text type.
- Do not “polish” so aggressively that gameplay meaning changes.
- Avoid unnatural Chinese syntax, redundant subjects, literal classifier wording, and dictionary-like compounds.

### 3. Game terminology and named concepts

Use this precedence:

1. accepted player-facing forms in `glossary/ui_community_terms.json`;
2. exact canonical individual-skill examples in `glossary/skill_name_style.json`;
3. locked matching entries in `glossary/term_registry.json` unless overridden by 1-2;
4. established official/player-facing English/Romanized Uma Musume terminology;
5. natural Vietnamese only for genuinely generic concepts.

Never mechanically calque an unfamiliar named mechanic from Chinese. If the repository does not resolve it and reliable evidence is unavailable, `defer`.

For any item carrying `locked_terms`, `community_terms`, or `skill_name_canonical`, `keep`/`revise` requires `terminology_basis`. The merge validator rejects known forbidden calques, missing required player-facing forms, locked-term regressions, and conflicting exact skill-title examples.

### 4. Character identity and voice

When an item is attributable to a character or speaker:

- use `characters.json` for identity/name handling;
- use `speech_bible.json`, `speech_samples.json`, and `speech_evidence.json` for voice, register, pronouns, politeness, quirks, and relationship evidence;
- do not invent a speech rule when the speaker/context is not identifiable;
- optionally record `speech_basis` in the decision when voice evidence materially affected the judgment.

A generic one-size-fits-all `tôi/bạn` voice is not acceptable when repository evidence says otherwise.

### 5. Structural integrity

Any revision must preserve exactly:

- placeholders;
- printf tokens;
- runtime/rich-text tags;
- escaped runtime sequences;
- newline count/structure.

The merge validator runs structural QA before accepting a revision.

### 6. UI boundary

Translation review may fix semantic/terminology/naturalness problems in UI strings. It does not replace the fixed-control visual-fit pipeline in `UI_REVIEW.md`; clipping, width budgets, control type, and compact-layout decisions belong there.

## Atomic claiming

Read `work/translation_review/active_plan.json`. Work is assignable only when `status` is `active`.

Scan the referenced plan's batches in listed order. The plan is risk-prioritized while each batch preserves nearby source context.

A batch is available when:

- `work/translation_review/merged/<batch_id>.json` does not exist; and
- no live claim exists at `work/translation_review/claims/<batch_id>.json`.

Atomically create exactly one claim:

`work/translation_review/claims/<batch_id>.json`

Example:

```json
{
  "schema_version": 1,
  "plan_id": "tr-p1-...",
  "batch_id": "tr-p1-...-b0001",
  "claim_id": "tr-sol-20260827T160000Z-a1b2c3",
  "worker_id": "ChatGPT",
  "claimed_at": "2026-08-27T16:00:00Z",
  "heartbeat_at": "2026-08-27T16:00:00Z",
  "expires_at": "2026-08-27T16:45:00Z"
}
```

Never overwrite another live claim. Expired claims may be taken over using optimistic concurrency. Heartbeat only your own claim.

## Decisions

Every item must receive exactly one:

- `keep` — the current target passes all applicable gates;
- `revise` — provide a corrected target;
- `defer` — evidence/context is insufficient; this remains unresolved and continues blocking the global gate.

Low-confidence corrections must `defer`, not `revise`.

Write:

`work/translation_review/results/<batch_id>/<claim_id>.json`

Example:

```json
{
  "schema_version": 1,
  "plan_id": "tr-p1-...",
  "batch_id": "tr-p1-...-b0001",
  "claim_id": "...",
  "worker_id": "ChatGPT",
  "reviewed_at": "...",
  "decisions": [
    {
      "uid": "zhcn:...",
      "current_fingerprint": "...",
      "action": "revise",
      "proposed_text": "Hero Gauge",
      "reason": "Current target is a literal calque of a named game mechanic.",
      "terminology_basis": "ui_community_terms:event.loh.hero_gauge",
      "confidence": "high"
    }
  ]
}
```

`reason` is required for every action. For `keep`, a concise reason such as `Faithful, natural, terminology and structure pass.` is sufficient. Omit `proposed_text` for `keep`/`defer`.

Before completion verify that decisions cover all and only assigned UIDs exactly once.

## Completion

After the result is committed, create:

`work/translation_review/completions/<batch_id>/<claim_id>.json`

```json
{
  "schema_version": 1,
  "plan_id": "...",
  "batch_id": "...",
  "claim_id": "...",
  "worker_id": "ChatGPT",
  "result_path": "work/translation_review/results/<batch_id>/<claim_id>.json",
  "completed_at": "..."
}
```

`.github/workflows/merge-translation-review.yml` validates decisions against the immutable plan and latest canonical target.

- changed target fingerprint -> whole batch is closed as `stale` and re-enters a later plan;
- changed review context/policy -> completion is `superseded`;
- `keep`/`revise` -> resolved in `reviewed_index.json`;
- `defer` -> recorded but deliberately re-enqueued.

After a plan is fully merged, the workflow immediately builds the next delta plan. Only an idle plan with zero unresolved entries clears `translation_review_gate` and re-enables translation claims.

## Ownership

Review workers never edit:

- `localized_data/**`;
- `work/merged/**`;
- `work/translation_progress.json`;
- canonical glossary/speech files;
- `work/translation_review/reviewed_index.json`;
- `work/parallel_state.json`.

Workers only write their own claim, result, heartbeat, and completion marker. The merge/sync workflows own canonical revisions, review index, plans, and gate state.

## Continuous loop

After completing a review batch:

1. re-read `work/translation_review/active_plan.json` from `main`;
2. claim the next available review batch;
3. continue while capacity remains.

Do not switch to new translation shards while the gate is enabled.

# Parallel translation review workers

This is the canonical retrospective QA protocol for translations already merged into Vietnamese.

The objective is high-quality review with **minimal startup context**. Do not bulk-read glossary, speech, character, or plan files unless the current batch actually needs them.

## Gate

`work/parallel_state.json.translation_review_gate` is authoritative.

While `enabled: true`:

- do not create or take over normal translation claims;
- review already merged translations only;
- existing translation progress is unchanged;
- `defer` is unresolved and keeps the gate closed.

The gate opens only when every canonical entry in review scope has a current `keep` or `revise` decision.

## Fast worker startup

Read only these from `main` before claiming:

1. `TRANSLATION_REVIEW.md`
2. `work/parallel_state.json`
3. `work/translation_review/active_plan.json`

Do **not** read the full plan file by default.
Do **not** pre-read `GAME_CONTEXT.md`, `term_registry.json`, `ui_community_terms.json`, `skill_name_style.json`, `characters.json`, or any speech file.

After selecting a candidate batch, read exactly that one batch file. A normal worker therefore starts with three small control files plus one 20-entry batch.

Repository state overrides chat history and model priors. Current Vietnamese text is a hypothesis, not evidence that it is correct.

## Choosing a batch without reading the full plan

`active_plan.json` provides `plan_id`, `batch_count`, `lease_minutes`, and a short `priority_batch_ids` list.

1. Try `priority_batch_ids` in order. For each id, skip it if `work/translation_review/merged/<batch_id>.json` exists or a live claim exists at `work/translation_review/claims/<batch_id>.json`.
2. If the priority head is busy, spread workers deterministically: hash your unique worker id, map it to `1..batch_count`, then probe forward cyclically.
3. Batch files are deterministic:
   `work/translation_review/batches/<plan_id>/<plan_id>-bNNNN.json`.
4. Atomically create one claim. Never overwrite another live claim.

There is no need to load `work/translation_review/plans/<plan_id>.json` during normal work.

## Context already embedded in each batch

Each item already contains source/current text, fingerprints, source path, structural identity, risk flags, and where applicable:

- `locked_terms`
- `community_terms`
- `skill_name_canonical`

Treat these embedded fields as the normal terminology context for that item. They are generated from the current policy snapshot.

If `community_terms` contains accepted/forbidden forms and a basis, **do not reopen the whole community-term registry just to confirm the same data**.
If `skill_name_canonical` is present, use that exact mapping without rereading the whole skill-style file.
If `locked_terms` is present, use the embedded matching locked terms unless a higher-precedence embedded community/skill rule overrides them.

## Lazy context: fetch only when needed

Open extra repository context only for an item that cannot be safely judged from the batch itself.

### Unknown game mechanic / unresolved terminology

Only then search targeted records in:

- `glossary/ui_community_terms.json`
- `glossary/term_registry.json`
- `glossary/skill_name_style.json`
- `GAME_CONTEXT.md`

Search for the exact source term/name. Do not read every file end-to-end.

Terminology precedence:

1. embedded/player-facing `community_terms`;
2. embedded exact `skill_name_canonical`;
3. locked registry terms not overridden by 1-2;
4. established official/player-facing English or Romanized Uma Musume terminology;
5. natural Vietnamese only for genuinely generic concepts.

Examples: `Speed`, `Stamina`, `Power`, `Guts`, `Wit`, generic `Skill`, `Hero Gauge`, `Hero Skill`, `League of Heroes` stay in their approved player-facing forms when matched.

### Proper name

Only if identity is uncertain, search the exact source alias in `glossary/characters.json`. Do not load the entire character registry preemptively. Never semantically translate a Chinese character/racehorse proper name.

### Character dialogue / voice

Only when an item is clearly attributable to a speaker **and voice affects the decision**, search the relevant speaker/relationship record in:

- `glossary/speech_bible.json`
- `glossary/speech_samples.json`
- `glossary/speech_evidence.json`
- `glossary/characters.json`

Use targeted search for that speaker/name. Do not read all speech profiles for ordinary system/UI/skill text.

If the speaker cannot be identified reliably and the current wording depends on speaker-specific pronouns/register, use `defer` rather than loading unrelated context or inventing a rule.

## Review gates

For every assigned item check:

1. **Meaning** — no changed subject/object, polarity, condition, quantity, implication, omission, or unsupported addition.
2. **Natural Vietnamese** — shipped-game quality, not Chinese word order or dictionary glosses.
3. **Terminology** — obey embedded/current player-facing terminology and individual-skill naming policy.
4. **Identity/voice** — only when applicable; use lazy targeted context above.
5. **Structure** — revisions preserve placeholders, printf tokens, tags, escaped runtime tokens, and newline structure exactly.

Translation review may repair semantic/naturalness issues in UI text, but fixed-control width/clipping belongs to `UI_REVIEW.md`.

## Decisions

Every and only every assigned UID gets exactly one action:

- `keep` — current text passes all applicable gates;
- `revise` — provide a confident correction;
- `defer` — evidence is insufficient; remains unresolved.

Low-confidence correction => `defer`, never guess.

For `keep`/`revise`, if the item has `locked_terms`, `community_terms`, or `skill_name_canonical`, include non-empty `terminology_basis`.

## Claim

Create:

`work/translation_review/claims/<batch_id>.json`

with exact active `plan_id`/`batch_id`, unique `claim_id`, worker id, UTC timestamps, and `expires_at` using `lease_minutes` from `active_plan.json`.

Heartbeat only your own claim.

## Result

Write:

`work/translation_review/results/<batch_id>/<claim_id>.json`

```json
{
  "schema_version": 1,
  "plan_id": "...",
  "batch_id": "...",
  "claim_id": "...",
  "worker_id": "ChatGPT",
  "reviewed_at": "...",
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

Cover all and only batch UIDs exactly once. Omit `proposed_text` for keep/defer.

## Completion

Only after the result is saved, create:

`work/translation_review/completions/<batch_id>/<claim_id>.json`

with `plan_id`, `batch_id`, `claim_id`, `worker_id`, exact `result_path`, and UTC `completed_at`.

The merge workflow validates fingerprint freshness, terminology, skill-title constraints, and structural QA. Stale/context-old work is not applied.

## Ownership

Review workers edit only their own claim/result/completion (and their own claim heartbeat).

Never directly edit:

- `localized_data/**`
- `work/merged/**`
- `work/translation_progress.json`
- `work/parallel_state.json`
- `work/translation_review/reviewed_index.json`
- canonical glossary/speech files

## Continuous loop

After each completion:

1. re-read only `work/translation_review/active_plan.json` and `work/parallel_state.json`;
2. if the plan changed, use the new plan id;
3. claim another available batch using `priority_batch_ids`, then hashed fallback;
4. do not reread this protocol unless its policy/version changed;
5. stop when the gate clears or no useful capacity remains.

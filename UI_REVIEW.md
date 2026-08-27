# Parallel UI review workers

This is a dedicated retrospective UI-quality pipeline. It is independent from translation batches and from speech/terminology curation.

## Purpose

Review **already translated fixed-size UI text** in `localized_data/localize_dict.json` for two independent quality gates:

1. **game-language correctness** — mechanic/event/mode/resource names must match the repository's locked terminology or the established player-facing Uma Musume term; do not invent Vietnamese semantic calques from Chinese wording;
2. **visual correctness** — labels must fit their controls without clipping, excessive best-fit shrinking, awkward wrapping, redundant wording, slash compounds, or untranslated JP/zh leakage.

A string is not QA-passed merely because its Vietnamese meaning is understandable.

Do not use this pipeline for story dialogue, character dialogue, lyrics, race commentary, or long prose.

## Policy generation

**UI review policy v3 is a clean semantic/community reset.** Results from policy v1/v2 do not count as completed v3 review. The plan builder intentionally re-enqueues unchanged fixed-size UI that was only reviewed under an older policy.

Old v2 claims/results/completions must not be reused as authority. The merge pipeline marks unmerged pre-v3 completions as `superseded` instead of applying them.

## Mandatory context

Before claiming work, read from `main`:

1. `UI_REVIEW.md`
2. `UI_TRANSLATION_RULES.md`
3. `glossary/term_registry.json`
4. `glossary/ui_community_terms.json`
5. `glossary/ui_short_forms.json`
6. `glossary/ui_overrides.json`
7. `glossary/style_rules.json`
8. `GAME_CONTEXT.md`
9. `work/ui_review/active_plan.json`
10. the active plan referenced by it
11. the specific batch file referenced by that plan

Repository state overrides chat history and model priors.

## Terminology gate

Treat the current Vietnamese text as a **hypothesis**, never as evidence that a term is correct.

Before choosing `keep` or `revise`, identify whether the source contains a named game mechanic, event, mode, stage, gauge, resource, skill family, race format, or other player-facing proper term.

Use this precedence:

1. a locked matching entry in `glossary/term_registry.json`;
2. an accepted player-facing form in `glossary/ui_community_terms.json`;
3. an official in-game English/Romanized term or strongly established Uma Musume player shorthand;
4. a natural Vietnamese translation only when the concept is genuinely generic.

Do **not** mechanically translate a named mechanic from Chinese. Examples of prohibited regressions include `英雄量表 -> Thanh Anh hùng` and `英雄技能 -> Kỹ năng Anh hùng` when the player-facing mechanic is `Hero Gauge` / `Hero Skill`.

If a named mechanic is unfamiliar and the repository does not resolve it, research reliable official/player-guide evidence when tools are available. If the evidence is still weak, use `defer`; do not invent a canonical Vietnamese term.

For any batch item whose `community_terms` array is non-empty, a `keep` or `revise` decision must include a non-empty `terminology_basis`. The merge validator also rejects known forbidden calques and requires an accepted player-facing form when the matched term says `require_accepted: true`.

## Ownership rule

UI review workers **never edit**:

- `localized_data/**`
- `glossary/ui_overrides.json`
- `glossary/ui_short_forms.json`
- `glossary/ui_community_terms.json`
- `glossary/term_registry.json`
- `work/ui_review/reviewed_index.json`
- translation progress, translation results, or curation canonical files

Workers only write their own claim, result, heartbeat updates, and completion marker. `.github/workflows/merge-ui-review.yml` exclusively applies accepted revisions.

## Atomic claiming

Read `work/ui_review/active_plan.json`. If its status is not `active`, there is currently no assignable UI review work.

Read the referenced plan and scan its batches in order. A batch is available when:

- `work/ui_review/merged/<batch_id>.json` does not exist, and
- no valid non-expired claim exists at `work/ui_review/claims/<batch_id>.json`.

Atomically create exactly one claim at:

`work/ui_review/claims/<batch_id>.json`

Claim schema:

```json
{
  "schema_version": 1,
  "plan_id": "...",
  "batch_id": "ui-p3-...-b0001",
  "claim_id": "ui-gpt-20260827T143000Z-a1b2c3",
  "worker_id": "ChatGPT",
  "claimed_at": "2026-08-27T14:30:00Z",
  "heartbeat_at": "2026-08-27T14:30:00Z",
  "expires_at": "2026-08-27T15:15:00Z"
}
```

Use the exact `plan_id` and lease duration from the active plan. Never overwrite another worker's live claim. If another worker wins the create race, immediately try another batch.

Heartbeat long work by updating only your own claim while preserving `plan_id`, `batch_id`, `claim_id`, and `worker_id`.

## Reviewing a batch

Every assigned item contains the source text, current Vietnamese text, key/path, fingerprints, approximate visual widths, automatic risk hints, and—when recognized—`community_terms`.

For **every item**, choose exactly one action:

- `keep` — current text passes both terminology/game-language QA and visual QA.
- `revise` — replace it with a better player-facing and compact UI form.
- `defer` — terminology or layout/context is too uncertain to safely decide.

Review all and only items assigned to the batch.

### Visual correctness

Follow `UI_TRANSLATION_RULES.md`. In particular:

- semantic correctness alone is not enough for fixed controls;
- prefer 1–3 short words for small buttons/tabs/menu tiles;
- remove context already obvious from the screen or icon;
- avoid slash-separated synonym piles;
- do not add a newline merely to rescue a long translation;
- preserve the source newline count and all runtime syntax;
- a translation that protrudes, clips, wraps to an extra line, or forces extreme shrinking is not QA-passed;
- do not shorten so aggressively that the game action or mechanic changes meaning.

Automatic `risk_flags` are hints, not verdicts. `community_calque_risk` and `community_term_mismatch` are high-priority semantic warnings.

### `revise` requirements

A revision must:

- be non-empty natural player-facing Vietnamese/UI language;
- preserve placeholders, printf tokens, markup tags, escaped runtime tokens, and source newline count;
- preserve canonical game terms and accepted community-facing mechanic names;
- be at least as clear in the current UI context;
- normally be no wider than the current text and preferably fit the budget in `UI_TRANSLATION_RULES.md`;
- use canonical compact forms where applicable;
- have `confidence` `high` or `medium`.

If confidence is `low`, use `defer`, not `revise`.

## Result

After reviewing all items, write exactly one claim-scoped result:

`work/ui_review/results/<batch_id>/<claim_id>.json`

Schema:

```json
{
  "schema_version": 1,
  "plan_id": "...",
  "batch_id": "ui-p3-...-b0001",
  "claim_id": "...",
  "worker_id": "ChatGPT",
  "reviewed_at": "...",
  "decisions": [
    {
      "key": "Heroes511003",
      "current_fingerprint": "...",
      "action": "revise",
      "proposed_text": "Chi tiết Hero Gauge",
      "control_type": "header",
      "reason": "The current text calques a named LoH mechanic; use the player-facing mechanic name.",
      "terminology_basis": "ui_community_terms:event.loh.hero_gauge",
      "confidence": "high"
    }
  ]
}
```

For `keep`, omit `proposed_text`. For `defer`, explain the missing context briefly. `control_type` may be `unknown` rather than guessed.

Before completion verify:

- decisions cover ALL AND ONLY batch keys exactly once;
- every `current_fingerprint` exactly matches the batch item;
- every matched `community_terms` item has terminology checked before `keep`/`revise`;
- no known forbidden calque survives a `keep`/`revise`;
- no revision changes placeholders/tags/newline structure;
- no revision expands a reviewed compact label without evidence;
- no story/prose rewriting was introduced.

## Completion

After the result is committed, create:

`work/ui_review/completions/<batch_id>/<claim_id>.json`

```json
{
  "schema_version": 1,
  "plan_id": "...",
  "batch_id": "ui-p3-...-b0001",
  "claim_id": "...",
  "worker_id": "ChatGPT",
  "result_path": "work/ui_review/results/ui-p3-...-b0001/<claim_id>.json",
  "completed_at": "..."
}
```

The merge workflow validates the result against the immutable plan batch. If the underlying UI text changed after the plan snapshot, the batch is closed as stale and those changed keys are automatically eligible for a later plan instead of applying stale edits.

## Continuous loop

After completing a batch:

1. re-read `work/ui_review/active_plan.json` from `main`;
2. claim another available UI batch;
3. continue while useful capacity remains.

Do not switch to speech/terminology or translation batches while acting as a UI review worker.

At session end report only: batches completed, keep/revise/defer counts, and blockers.

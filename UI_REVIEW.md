# Parallel UI review workers

This is a dedicated retrospective UI-quality pipeline. It is independent from translation batches and from speech/terminology curation.

## Purpose

Review **already translated fixed-size UI text** in `localized_data/localize_dict.json` and correct labels that are semantically acceptable but visually poor in game: overflow, excessive best-fit shrinking, awkward wrapping, redundant wording, slash compounds, or untranslated JP/zh leakage.

Do not use this pipeline for story dialogue, character dialogue, lyrics, race commentary, or long prose.

## Mandatory context

Before claiming work, read from `main`:

1. `UI_REVIEW.md`
2. `UI_TRANSLATION_RULES.md`
3. `glossary/ui_short_forms.json`
4. `glossary/ui_overrides.json`
5. `glossary/style_rules.json`
6. `GAME_CONTEXT.md`
7. `work/ui_review/active_plan.json`
8. the active plan referenced by it
9. the specific batch file referenced by that plan

Repository state overrides chat history and model priors.

## Ownership rule

UI review workers **never edit**:

- `localized_data/**`
- `glossary/ui_overrides.json`
- `glossary/ui_short_forms.json`
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
  "batch_id": "ui-00001",
  "claim_id": "ui-gpt-20260826T143000Z-a1b2c3",
  "worker_id": "ChatGPT",
  "claimed_at": "2026-08-26T14:30:00Z",
  "heartbeat_at": "2026-08-26T14:30:00Z",
  "expires_at": "2026-08-26T15:15:00Z"
}
```

Use the exact `plan_id` and lease duration from the active plan. Never overwrite another worker's live claim. If another worker wins the create race, immediately try another batch.

Heartbeat long work by updating only your own claim while preserving `plan_id`, `batch_id`, `claim_id`, and `worker_id`.

## Reviewing a batch

Every assigned item contains the source text, current Vietnamese text, key/path, fingerprints, approximate visual widths, and automatic risk hints.

For **every item**, choose exactly one action:

- `keep` — current Vietnamese is already natural, compact, and visually safe.
- `revise` — replace it with a better compact Vietnamese UI form.
- `defer` — layout/context is too uncertain to safely decide without stronger evidence such as a screenshot.

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

Automatic `risk_flags` are hints, not verdicts. Review the actual source/current text.

### `revise` requirements

A revision must:

- be non-empty natural Vietnamese;
- preserve placeholders, printf tokens, markup tags, escaped runtime tokens, and source newline count;
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
  "batch_id": "ui-00001",
  "claim_id": "...",
  "worker_id": "ChatGPT",
  "reviewed_at": "...",
  "decisions": [
    {
      "key": "Menu0004",
      "current_fingerprint": "...",
      "action": "revise",
      "proposed_text": "Tủ cúp",
      "control_type": "menu_tile",
      "reason": "Current label is unnecessarily wide for a fixed menu tile.",
      "confidence": "high"
    }
  ]
}
```

For `keep`, omit `proposed_text`. For `defer`, explain the missing context briefly. `control_type` may be `unknown` rather than guessed.

Before completion verify:

- decisions cover ALL AND ONLY batch keys exactly once;
- every `current_fingerprint` exactly matches the batch item;
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
  "batch_id": "ui-00001",
  "claim_id": "...",
  "worker_id": "ChatGPT",
  "result_path": "work/ui_review/results/ui-00001/<claim_id>.json",
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

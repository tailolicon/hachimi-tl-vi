# Canonical finding research — 料理Pt

Finding: `cf-9c3a9ad76cae6fe6`

## Evidence and diagnosis

Repeated retrospective review evidence identifies `料理Pt` as a reusable player-facing system label in the `収穫ッ！満腹ッ！大豊食祭` cooking scenario. Existing review results have deferred affected strings instead of guessing a one-off Vietnamese rendering.

Fresh identity research confirms the underlying JP mechanic is consistently presented as `お料理Pt` / `料理Pt`. Japanese scenario coverage describes gaining and meeting thresholds in `お料理Pt`, while the established English community reference GameTora calls the same quantity **Cooking Points** throughout its Great Food Festival scenario guide (for example dishes award +250/+500/+800/+1000 Cooking Points).

This is therefore not generic prose meaning “food points”; it is a scenario resource/score label. A systemic canonical rule is warranted rather than patching review items individually.

## Proposed canonical direction

Use **`Cooking Points`** as the English player-facing identity for the mechanic unless repository precedent requires preserving the abbreviated `Pt` surface form per exact UI string. Keep matching narrowly scoped to cooking-scenario UI / known `料理Pt` occurrences so generic `料理` prose cannot be captured.

Before production acceptance, inspect the live finding shape and affected keys, add an idempotent hardener plus positive/negative regression coverage, then run Validate and production Sync translation context followed by an unchanged no-op Sync. Do not edit `localized_data/**` directly.

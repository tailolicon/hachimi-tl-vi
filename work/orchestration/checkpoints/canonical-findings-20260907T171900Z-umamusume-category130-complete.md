# Canonical finding complete — category-130 马娘 shorthand

Claim: `canonical-findings-maintenance-gpt56sol-auto11-20260907T170817Z`
Finding: `cf-93e25a8c1b655cdc`

## Production result

Category-130 `马娘` is now canonically resolved to **Mã Nương** through the permanent, item-scoped term `common.world.umamusume.training_shorthand`.

The alias is deliberately limited to `text_data_dict.json` category `130` with `match_mode: contains`; it is not globalized and does not overlap the existing category-144 profile shorthand rule.

## Durable source

- hardener: `5d8307f54267730bc81b52d35b58a52d5a6b265b`;
- regression: `11828ff403da81a1a4b06384cbe6137800913495`;
- generated context commit: `3a7b6f40b271cac56b5532207dba7dd378aa7134`.

## Acceptance

- production Context Sync `34146463176` succeeded, passed 837 tests and persisted the scoped rule;
- unchanged Context Sync `34146485793` / job `101820140150` succeeded, passed **839 tests**, reported the category-130 hardener `changed=false` on both hardener passes, and ended with exactly `Context is already current.`;
- production retrospective review-plan run `34146463147` / job `101819464794` succeeded after detecting concurrent canonical input movement and rebuilding from fresh `main`;
- the fresh rebuild passed **839 tests** and published plan `tr-p3-67f8551f7780-cc36ed4d35d6-b5c0bcb3bd-c74ac85928` with 2,941 candidates / 148 batches;
- live `work/parallel_state.json` points to that plan;
- exact search of the new plan namespace for `cf-93e25a8c1b655cdc` returns no worker-facing match. Historical result/checkpoint records retain the finding id as audit history, which is expected.

This finding satisfies the canonical-maintenance acceptance chain and may increment maintenance `completed_count` from **197 to 198**.

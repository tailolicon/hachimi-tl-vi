# canonical-character-training-ui W2 checkpoint — 2026-08-29T16:17Z

## Ownership and replay

- Claim: `canonical-character-training-ui-w2-20260829T1606Z`.
- Domain branch: `canonical-character-training-ui-hardening`.
- W2 replayed the permanent Character/Training UI hardener and regression files onto then-live `main` after Training/Support finalization advanced `main`; replay commit: `f837df4509ebcdc5b324c7e9d8fbe96bc88985a3`.
- A later branch commit `941378b4cfa5ef8abf960646c2744990d65d3110` removed one focused test whose assertion depended on a predecessor Race live-materialization behavior rather than Character hardener output. W2 preserved that branch commit rather than overwriting concurrent branch work.

## Fresh execution evidence

GitHub Actions run `33262472966` on the replayed branch established:

- `python scripts/harden_character_training_ui_canon.py` succeeds.
- A second unchanged hardener run produces an identical diff: idempotence PASS.
- Focused Character suite: **19 passed**.
- Full pytest: **215 passed, 2 failed**. Both failures are live-orchestration invariant failures, not Character assertions:
  - `tests/test_orchestration_finalization.py::test_live_orchestration_state_has_explicit_valid_stage`
  - `tests/test_orchestration_state.py::test_parallel_canonical_tasks_have_independent_claim_files`
- Root cause visible on live `main`: `active_task` still names `canonical-training-support` while that roadmap item is already `status=complete, stage=complete`. The serial primary lane must repair/advance orchestration before a full-suite green proof is possible.
- `tlvi validate`: PASS (`ok=true`, no errors/warnings).
- `tlvi index`: PASS, 8 files indexed.

## Materialization proof (not yet persisted)

The hardener deterministically produces only the expected Character-domain changes:

- append scoped locked entries for `career.ui.mode`, `career.ui.trainee`, `career.ui.goal_race`, `career.ui.turn`, `career.ui.rating`, `career.ui.team_rating`, `career.ui.scenario`, and `race.ui.track.room_match` to `glossary/term_registry.json`;
- add `育成赛马娘` and `育成\n赛马娘` exclusions to `common.world.umamusume` in `glossary/ui_community_terms.json`;
- add the same two exclusions to `BRAND_EXCLUSIONS` in `scripts/enforce_player_facing_canon.py`.

Those generated changes were intentionally **not** persisted yet because the full suite cannot be made green until live orchestration is repaired, and secondary domain work must not claim readiness without fresh replay/materialization/validation against the corrected `main`.

## Predecessor Race observation

The live materialized `race.class.junior.ui` record contains `source_paths=[localize_dict.json]`, exact keys including `SingleMode0017`, but also text-data `json_path_prefixes` (`32`, `33`, `111`). Under the current matcher that combination does not match the expected `SingleMode0017` localize slot. This is predecessor/live materialization behavior, not introduced by the Character hardener. Do not silently fold a Race-domain repair into Character integration; verify it in the appropriate serial/final-conflict path.

## Handoff

1. Primary integration lane must first repair/advance live orchestration away from completed `canonical-training-support` according to `WORKER_START.md`/`AUTOPILOT.md`.
2. Refetch corrected live `main` and replay Character branch if `main` advanced.
3. Rerun hardener twice, focused suite, full pytest, `tlvi validate`, and `tlvi index`.
4. Persist the deterministic materialized Character changes only after that fresh green proof.
5. Do not mark `canonical-character-training-ui` `ready_for_integration` until materialization is durable and full validation is green.

# Canonical findings maintenance checkpoint — Natsuki NPC item ignore pending acceptance

Finding `cf-c1b8c2da5791de2e` covers source `菜月(NPC)`. The existing rendering `Natsuki (NPC)` is plausible, but repository evidence does not establish the intended Japanese reading authoritatively enough for reusable canonical terminology.

## Scope evidence

The stable `text_data_dict.json` category-152 NPC layout contains this source identity at six repeated item paths:

- `152/10`
- `152/44`
- `152/78`
- `152/112`
- `152/146`
- `152/180`

Repository review artifacts independently expose these path positions; the current active plan `tr-p3-67f8551f7780-7ce4dfb45ab6-b5c0bcb3bd-734a4f22c0`, batch `b0137`, contains `152/180` with `current_text: Natsuki (NPC)` and the open finding `cf-c1b8c2da5791de2e`.

## Resolution implemented

- `scripts/harden_natsuki_npc_finding.py` — commit `2abba018865cbee33191b099417cd2f1688ad791`.
- `tests/test_natsuki_npc_finding_hardening.py` — commit `f5051c07778ecf74e6832111d4f78f3db3f5a19e`.
- Decision is `action=ignore`, `invalidation_scope=item`, `source_paths=[text_data_dict.json]`, `match_mode=exact`, with only the six exact paths above.
- Regression requires hardener idempotence, no canonical resolution, `review_resolution.action == ignore`, and removal from `active_findings()` after refresh.

This deliberately does **not** canonize `Natsuki` and does not broaden the ignore to category `152`.

## Acceptance gate

Production acceptance is pending. Require successful Validate, Sync translation context, and Sync translation review plan runs for/after the regression-test head, then verify regenerated worker-facing items no longer carry `cf-c1b8c2da5791de2e` before incrementing maintenance `completed_count` from 106 to 107.

### Durable acceptance progress

For head `f5051c07778ecf74e6832111d4f78f3db3f5a19e`:

- Validate run `33893500625` completed successfully.
- Sync translation review plan run `33893500425` is still in progress.
- Sync translation context run `33893500429` is still in progress; its `sync` job reached `Run all finding hardeners` after the preceding setup, identity sync, terminology extraction, finding-lock restoration, explicit terminology apply, audit hardening, and support-effect hardening steps all completed successfully.

Continuation: wait only on the two already-running production Sync workflows while doing protocol-valid maintenance investigation where safe. Once both succeed, verify the regenerated active plan/worker-facing item(s) no longer carry `cf-c1b8c2da5791de2e`; only then increment `completed_count` to 107 and continue to the next active finding. Do not canonize `Natsuki` and do not broaden category 152.
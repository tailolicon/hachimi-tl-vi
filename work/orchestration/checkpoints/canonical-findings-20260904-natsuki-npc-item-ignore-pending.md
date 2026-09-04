# Canonical findings maintenance checkpoint — Natsuki NPC item ignore accepted

Finding `cf-c1b8c2da5791de2e` covers source `菜月(NPC)`. The existing rendering `Natsuki (NPC)` is plausible, but repository evidence does not establish the intended Japanese reading authoritatively enough for reusable canonical terminology.

## Scope evidence

The stable `text_data_dict.json` category-152 NPC layout contains this source identity at six repeated item paths:

- `152/10`
- `152/44`
- `152/78`
- `152/112`
- `152/146`
- `152/180`

Repository review artifacts independently expose these path positions; the current active plan `tr-p3-67f8551f7780-7ce4dfb45ab6-b5c0bcb3bd-734a4f22c0`, batch `b0137`, contains `152/180` with `current_text: Natsuki (NPC)`.

## Resolution implemented

- `scripts/harden_natsuki_npc_finding.py` — commit `2abba018865cbee33191b099417cd2f1688ad791`.
- `tests/test_natsuki_npc_finding_hardening.py` — commit `f5051c07778ecf74e6832111d4f78f3db3f5a19e`.
- Decision is `action=ignore`, `invalidation_scope=item`, `source_paths=[text_data_dict.json]`, `match_mode=exact`, with only the six exact paths above.
- Regression requires hardener idempotence, no canonical resolution, `review_resolution.action == ignore`, and removal from `active_findings()` after refresh.

This deliberately does **not** canonize `Natsuki` and does not broaden the ignore to category `152`.

## Production acceptance

For head `f5051c07778ecf74e6832111d4f78f3db3f5a19e`:

- Validate run `33893500625` completed successfully.
- Sync translation review plan run `33893500425` completed successfully.
- Sync translation context run `33893500429` completed successfully.
- Live active-plan batch `b0137` now shows source `菜月(NPC)` at `text_data_dict.json` path `152/180` with `canonical_findings: []`.

Result: finding `cf-c1b8c2da5791de2e` is production-accepted as an exact item-scoped ignore. Maintenance completion may advance from 106 to 107. Continue with another active canonical finding; do not canonize `Natsuki`.
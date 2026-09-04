# Canonical findings maintenance checkpoint — Keisuke NPC item ignore accepted

Finding `cf-1edf7f36acfffbfb` covers source `圭介(NPC)`. The existing rendering `Keisuke (NPC)` is plausible, but repository evidence does not establish the intended Japanese reading authoritatively enough for reusable canonical terminology.

## Scope evidence

Review artifacts expose this source identity at six repeated `text_data_dict.json` category-152 item paths:

- `152/3`
- `152/37`
- `152/71`
- `152/105`
- `152/139`
- `152/173`

The current/live review family and historical plan evidence confirm the repeated 34-item stride rather than a category-wide semantic rule.

## Resolution implemented

- `scripts/harden_keisuke_npc_finding.py` — commit `210df019ac33c53f9c5faeb865dd2ebbd64beed7`.
- `tests/test_keisuke_npc_finding_hardening.py` — commit `4f0eef01d7bca1b9ab5e78871db9ec31016d32fa`.
- Decision is `action=ignore`, `invalidation_scope=item`, `source_paths=[text_data_dict.json]`, `match_mode=exact`, with only the six exact paths above.
- Regression requires hardener idempotence, no canonical resolution, `review_resolution.action == ignore`, and removal from `active_findings()` after refresh.

This deliberately does **not** canonize `Keisuke` and does not broaden the ignore to category `152`.

## Production acceptance

For regression head `4f0eef01d7bca1b9ab5e78871db9ec31016d32fa`:

- Validate run `33894181372` completed successfully.
- Sync translation context run `33894181432` completed successfully; its full finding-hardener/context pipeline passed.
- Sync translation review plan run `33894181496` completed successfully.
- Live active-plan batch `b0137` shows source `圭介(NPC)` at `text_data_dict.json` path `152/173` with `canonical_findings: []`.

Result: finding `cf-1edf7f36acfffbfb` is production-accepted as an exact item-scoped ignore. Maintenance completion advances from 107 to 108. Continue with `cf-6af810eb1dfb2be5` (`浩二(NPC)`), whose exact-scoped hardener and regression are already implemented and awaiting their production acceptance gates.
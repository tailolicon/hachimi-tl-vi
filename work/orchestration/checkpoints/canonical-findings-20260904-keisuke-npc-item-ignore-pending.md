# Canonical findings maintenance checkpoint — Keisuke NPC item ignore pending acceptance

Finding `cf-1edf7f36acfffbfb` covers source `圭介(NPC)`. The existing rendering `Keisuke (NPC)` is plausible, but repository evidence does not establish the intended Japanese reading authoritatively enough for reusable canonical terminology.

## Scope evidence

Review artifacts expose this source identity at six repeated `text_data_dict.json` category-152 item paths:

- `152/3`
- `152/37`
- `152/71`
- `152/105`
- `152/139`
- `152/173`

The current/live review family also exposes the same open finding on these NPC rows; historical plan evidence confirms the repeated 34-item stride rather than a category-wide semantic rule.

## Resolution implemented

- `scripts/harden_keisuke_npc_finding.py` — commit `210df019ac33c53f9c5faeb865dd2ebbd64beed7`.
- `tests/test_keisuke_npc_finding_hardening.py` — commit `4f0eef01d7bca1b9ab5e78871db9ec31016d32fa`.
- Decision is `action=ignore`, `invalidation_scope=item`, `source_paths=[text_data_dict.json]`, `match_mode=exact`, with only the six exact paths above.
- Regression requires hardener idempotence, no canonical resolution, `review_resolution.action == ignore`, and removal from `active_findings()` after refresh.

This deliberately does **not** canonize `Keisuke` and does not broaden the ignore to category `152`.

## Acceptance gate

Production acceptance is pending. Require successful Validate, Sync translation context, and Sync translation review plan runs for/after the regression-test head, then verify regenerated worker-facing items no longer carry `cf-1edf7f36acfffbfb` before incrementing maintenance `completed_count` from 107 to 108.

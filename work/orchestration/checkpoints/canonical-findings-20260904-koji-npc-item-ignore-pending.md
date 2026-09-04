# Canonical findings maintenance checkpoint — Koji NPC item ignore pending acceptance

Finding `cf-6af810eb1dfb2be5` covers source `浩二(NPC)`. Existing localized data uses `Koji (NPC)`, but repository evidence does not establish the intended Japanese reading authoritatively enough for reusable canonical terminology.

## Scope evidence

Review/source artifacts expose this source identity in the repeated `text_data_dict.json` category-152 NPC layout at six exact item paths:

- `152/4`
- `152/38`
- `152/72`
- `152/106`
- `152/140`
- `152/174`

Repository search evidence directly confirms later repeated positions including `38`, `72`, `106`, `140`, and current live active-plan item `174`; together with the stable 34-item NPC block cycle this identifies the exact six-item scope rather than a category-wide rule.

## Resolution implemented

- `scripts/harden_koji_npc_finding.py` — commit `4211ea083de6867fb2b32d12766a333385373e50`.
- `tests/test_koji_npc_finding_hardening.py` — commit `ebb111e0d1700eed053127ab42133f3585996970`.
- Decision is `action=ignore`, `invalidation_scope=item`, `source_paths=[text_data_dict.json]`, `match_mode=exact`, limited to the six exact paths above.
- Regression requires hardener idempotence, no `canonical_resolution`, `review_resolution.action == ignore`, and removal from `active_findings()` after refresh.

This deliberately does **not** canonize `Koji` and does not broaden the ignore to category `152`.

## Acceptance gate

Production acceptance is pending. Require successful Validate, Sync translation context, and Sync translation review plan runs for/after regression head `ebb111e0d1700eed053127ab42133f3585996970`, then verify regenerated worker-facing items no longer carry `cf-6af810eb1dfb2be5` before incrementing maintenance `completed_count` from 108 to 109.

The immediately preceding Keisuke finding `cf-1edf7f36acfffbfb` remains logically ahead in the completion sequence: its regression is already implemented and Validate succeeded, but its two Sync workflows must finish successfully and live output must be verified before `completed_count` can advance from 107 to 108.
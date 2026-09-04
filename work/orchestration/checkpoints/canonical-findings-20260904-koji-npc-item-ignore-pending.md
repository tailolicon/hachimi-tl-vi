# Canonical findings maintenance checkpoint — Koji NPC item ignore accepted

Finding `cf-6af810eb1dfb2be5` covers source `浩二(NPC)`. Existing localized data uses `Koji (NPC)`, but repository evidence does not establish the intended Japanese reading authoritatively enough for reusable canonical terminology.

## Scope evidence

Review/source artifacts expose this source identity in the repeated `text_data_dict.json` category-152 NPC layout at six exact item paths:

- `152/4`
- `152/38`
- `152/72`
- `152/106`
- `152/140`
- `152/174`

Repository search evidence directly confirms later repeated positions including `38`, `72`, `106`, `140`, and the live active-plan item `174`; together with the stable 34-item NPC block cycle this identifies the exact six-item scope rather than a category-wide rule.

## Resolution implemented

- `scripts/harden_koji_npc_finding.py` — commit `4211ea083de6867fb2b32d12766a333385373e50`.
- `tests/test_koji_npc_finding_hardening.py` — commit `ebb111e0d1700eed053127ab42133f3585996970`.
- Decision is `action=ignore`, `invalidation_scope=item`, `source_paths=[text_data_dict.json]`, `match_mode=exact`, limited to the six exact paths above.
- Regression requires hardener idempotence, no `canonical_resolution`, `review_resolution.action == ignore`, and removal from `active_findings()` after refresh.

This deliberately does **not** canonize `Koji` and does not broaden the ignore to category `152`.

## Production acceptance

For regression head `ebb111e0d1700eed053127ab42133f3585996970`:

- Validate run `33894508487` completed successfully.
- Sync translation review plan run `33894508475` completed successfully.
- Sync translation context run `33894508493` completed successfully; the finding-hardener and context pipeline passed.
- Live active-plan batch `b0137` shows source `浩二(NPC)` at `text_data_dict.json` path `152/174` with `canonical_findings: []`.

Result: finding `cf-6af810eb1dfb2be5` is production-accepted as an exact item-scoped ignore. Maintenance completion advances from 108 to 109. Continue with `cf-ad719284aacc4b7f` (`宗太(NPC)`), whose exact-scoped hardener and regression are already implemented and awaiting production acceptance.
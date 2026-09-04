# Canonical findings maintenance checkpoint — Sota NPC item ignore accepted

Finding `cf-ad719284aacc4b7f` covers source `宗太(NPC)`. Existing localized data uses `Sota (NPC)`, but the Japanese given-name spelling can admit reading/romanization ambiguity and repository evidence does not establish a reusable canonical reading authoritatively.

## Scope evidence

The stable `text_data_dict.json` category-152 NPC layout repeats this identity at six exact paths:

- `152/6`
- `152/40`
- `152/74`
- `152/108`
- `152/142`
- `152/176`

Review artifacts directly expose later repeated positions including `108`, `142`, and live item `176`; the fixed 34-item NPC block cycle supplies the corresponding exact repeated positions rather than a category-wide semantic rule.

## Resolution implemented

- `scripts/harden_sota_npc_finding.py` — commit `3b2709566fcad148344b5e1ec21b2e66e2eb7aa0`.
- `tests/test_sota_npc_finding_hardening.py` — commit `c9ebdb29d5348f04b4ac3b4d5294a0826b4257fa`.
- Decision is `action=ignore`, `invalidation_scope=item`, `source_paths=[text_data_dict.json]`, `match_mode=exact`, limited to the six exact paths above.
- Regression requires hardener idempotence, no `canonical_resolution`, `review_resolution.action == ignore`, and removal from `active_findings()` after refresh.

This deliberately does **not** canonize `Sota` and does not broaden the ignore to category `152`.

## Production acceptance

For regression head `c9ebdb29d5348f04b4ac3b4d5294a0826b4257fa`:

- Validate run `33894728379` completed successfully.
- Sync translation context run `33894728431` completed successfully.
- Sync translation review plan run `33894728359` completed successfully.
- Live active-plan batch `b0137` shows source `宗太(NPC)` at `text_data_dict.json` path `152/176` with `canonical_findings: []`.

Result: finding `cf-ad719284aacc4b7f` is production-accepted as an exact item-scoped ignore. Maintenance completion advances from 109 to 110. Continue with `cf-2d11e8b41c5d8527` (`太郎(NPC)`), whose exact-scoped hardener and regression are already implemented and awaiting production acceptance.
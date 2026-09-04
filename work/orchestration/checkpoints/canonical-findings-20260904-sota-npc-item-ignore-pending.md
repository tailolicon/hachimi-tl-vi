# Canonical findings maintenance checkpoint — Sota NPC item ignore pending acceptance

Finding `cf-ad719284aacc4b7f` covers source `宗太(NPC)`. Existing localized data uses `Sota (NPC)`, but the Japanese given-name spelling can admit reading/romanization ambiguity and repository evidence does not establish a reusable canonical reading authoritatively.

## Scope evidence

The stable `text_data_dict.json` category-152 NPC layout repeats this identity at six exact paths:

- `152/6`
- `152/40`
- `152/74`
- `152/108`
- `152/142`
- `152/176`

Review artifacts directly expose later repeated positions including `108`, `142`, and the current live active-plan item `176`; the fixed 34-item NPC block cycle supplies the corresponding exact repeated positions rather than a category-wide semantic rule.

## Resolution implemented

- `scripts/harden_sota_npc_finding.py` — commit `3b2709566fcad148344b5e1ec21b2e66e2eb7aa0`.
- `tests/test_sota_npc_finding_hardening.py` — commit `c9ebdb29d5348f04b4ac3b4d5294a0826b4257fa`.
- Decision is `action=ignore`, `invalidation_scope=item`, `source_paths=[text_data_dict.json]`, `match_mode=exact`, limited to the six exact paths above.
- Regression requires hardener idempotence, no `canonical_resolution`, `review_resolution.action == ignore`, and removal from `active_findings()` after refresh.

This deliberately does **not** canonize `Sota` and does not broaden the ignore to category `152`.

## Acceptance gate

Production acceptance is pending. Require successful Validate, Sync translation context, and Sync translation review plan runs for/after regression head `c9ebdb29d5348f04b4ac3b4d5294a0826b4257fa`, then verify regenerated worker-facing items no longer carry `cf-ad719284aacc4b7f`. Completion sequencing remains ordered: Koji must first advance maintenance 108->109 after its own acceptance, then Sota may advance 109->110.
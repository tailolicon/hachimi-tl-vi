# Canonical findings maintenance checkpoint — Yoshiko NPC item ignore pending acceptance

Finding `cf-53209016ce00c5d2` covers source `佳子(NPC)`. Existing localized data uses `Yoshiko (NPC)`, but repository evidence explicitly records that `佳子` can also have other readings such as `Kako`; the zh-CN source has no furigana. This is not strong enough to promote `Yoshiko` into reusable canonical terminology.

## Scope evidence

Pinned source/review data shows the stable category-152 NPC block repeats this identity at the six exact paths:

- `152/21`
- `152/55`
- `152/89`
- `152/123`
- `152/157`
- `152/191`

The later positions `89`, `123`, `157`, and live `191` are directly exposed in review/source artifacts, and the category's fixed 34-item repeat identifies the paired earlier positions `21` and `55`. This is an item set, not a category-wide semantic rule.

## Resolution implemented

- `scripts/harden_yoshiko_npc_finding.py` — commit `dbe92a65a6f415875efab6d8f9db7518956023d4`.
- `tests/test_yoshiko_npc_finding_hardening.py` — commit `ba9c914e579fe281709eb7ce399190431e2dfffc`.
- Decision is `action=ignore`, `invalidation_scope=item`, `source_paths=[text_data_dict.json]`, `match_mode=exact`, limited to the six exact paths above.
- Regression requires hardener idempotence, no `canonical_resolution`, `review_resolution.action == ignore`, and removal from `active_findings()` after refresh.

This deliberately does **not** canonize `Yoshiko` and does not broaden the ignore to category `152`.

## Acceptance gate

Production acceptance is pending. Require successful Validate, Sync translation context, and Sync translation review plan runs for/after regression head `ba9c914e579fe281709eb7ce399190431e2dfffc`, then verify regenerated worker-facing items no longer carry `cf-53209016ce00c5d2` (at minimum live `152/191`, and an earlier repeated item when available) before incrementing maintenance `completed_count` from 112 to 113.
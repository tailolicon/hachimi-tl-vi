# Canonical findings maintenance checkpoint — Tsukasa NPC item ignore pending acceptance

Finding `cf-bde1cb5a78cf5e14` covers source `司(NPC)`. Existing localized data uses `Tsukasa (NPC)`, but `司` admits multiple Japanese readings and repository evidence does not establish a reusable canonical reading authoritatively.

## Scope evidence

The stable `text_data_dict.json` category-152 NPC layout repeats this identity at six exact paths:

- `152/8`
- `152/42`
- `152/76`
- `152/110`
- `152/144`
- `152/178`

Review artifacts directly expose current/live position `178`; the fixed 34-item NPC block cycle identifies the corresponding repeated positions without broadening the rule to category `152`.

## Resolution implemented

- `scripts/harden_tsukasa_npc_finding.py` — commit `6beac381437560c5df0b019bd571813b41b45bb7`.
- `tests/test_tsukasa_npc_finding_hardening.py` — commit `00aebf597823cf41b01caa88ba889d982882643d`.
- Decision is `action=ignore`, `invalidation_scope=item`, `source_paths=[text_data_dict.json]`, `match_mode=exact`, limited to the six exact paths above.
- Regression requires hardener idempotence, no `canonical_resolution`, `review_resolution.action == ignore`, and removal from `active_findings()` after refresh.

This deliberately does **not** canonize `Tsukasa` and does not broaden the ignore to category `152`.

## Acceptance gate

Production acceptance is pending. Require successful Validate, Sync translation context, and Sync translation review plan runs for/after regression head `00aebf597823cf41b01caa88ba889d982882643d`, then verify regenerated worker-facing items no longer carry `cf-bde1cb5a78cf5e14`. Completion sequencing remains ordered: Taro must first advance maintenance 110->111 after its acceptance, then Tsukasa may advance 111->112.
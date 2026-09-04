# Canonical findings maintenance checkpoint — Taro NPC item ignore pending acceptance

Finding `cf-2d11e8b41c5d8527` covers source `太郎(NPC)`. Existing localized data uses `Taro (NPC)`, but the repository does not establish a reusable canonical romanization strongly enough to promote this anonymous NPC display name into shared terminology.

## Scope evidence

The stable `text_data_dict.json` category-152 NPC layout repeats this identity at six exact paths:

- `152/7`
- `152/41`
- `152/75`
- `152/109`
- `152/143`
- `152/177`

Review artifacts directly expose positions `109`, `143`, and current/live `177`; the stable 34-item NPC block cycle identifies the corresponding earlier repeated positions without broadening the rule to category `152`.

## Resolution implemented

- `scripts/harden_taro_npc_finding.py` — commit `2afbc44b1b152ccc21430eeb37bb47acc129cb49`.
- `tests/test_taro_npc_finding_hardening.py` — commit `5b47f414ab807a5420944d078c38d1c7944dc55a`.
- Decision is `action=ignore`, `invalidation_scope=item`, `source_paths=[text_data_dict.json]`, `match_mode=exact`, limited to the six exact paths above.
- Regression requires hardener idempotence, no `canonical_resolution`, `review_resolution.action == ignore`, and removal from `active_findings()` after refresh.

This deliberately does **not** canonize `Taro` and does not broaden the ignore to category `152`.

## Acceptance gate

Production acceptance is pending. Require successful Validate, Sync translation context, and Sync translation review plan runs for/after regression head `5b47f414ab807a5420944d078c38d1c7944dc55a`, then verify regenerated worker-facing items no longer carry `cf-2d11e8b41c5d8527`. Completion sequencing remains ordered: Sota must first advance maintenance 109->110 after its acceptance, then Taro may advance 110->111.
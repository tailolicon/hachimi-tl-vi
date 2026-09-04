# Canonical findings maintenance checkpoint — Yoshiko NPC scoped ignore implemented

Finding `cf-53209016ce00c5d2` covers source `佳子(NPC)`. Existing localized data renders this as `Yoshiko (NPC)`, but `佳子` has multiple valid Japanese readings and repository evidence does not establish one reusable canonical reading authoritatively.

## Scope evidence

Live review artifacts expose this identity inside the stable category-152 NPC cycle, including exact path `152/21` and `152/89`; the current maintenance continuation identifies live path `152/191`. The established 34-item repeated NPC layout yields the six exact positions for this identity:

- `152/21`
- `152/55`
- `152/89`
- `152/123`
- `152/157`
- `152/191`

The resolution deliberately does not broaden to all category `152` items.

## Durable implementation now on main

- `scripts/harden_yoshiko_npc_finding.py` defines an `action=ignore`, `invalidation_scope=item`, `match_mode=exact` decision restricted to those six paths.
- `tests/test_yoshiko_npc_finding_hardening.py` requires exact scope, idempotence, no `canonical_resolution`, `review_resolution.action == ignore`, and removal from `active_findings()` after refresh.

This does **not** canonize `Yoshiko` or `Kako`. Production validation and Sync acceptance are still required before counting the finding complete.

# Canonical findings maintenance checkpoint — Kazuki NPC scoped ignore implemented

Finding `cf-903f94a51b0e869e` covers source `和树(NPC)`. Existing localized data renders this as `Kazuki (NPC)`, but repository evidence does not establish that reading authoritatively enough to promote it as reusable canonical terminology.

## Exact live scope

The repeated category-152 NPC layout and review artifacts establish the six exact items:

- `text_data_dict.json` `152/2`
- `152/36`
- `152/70`
- `152/104`
- `152/138`
- `152/172`

The resolution deliberately does not match the entire category `152`.

## Durable implementation on main

- `scripts/harden_kazuki_npc_finding.py` defines an `action=ignore`, `invalidation_scope=item`, `match_mode=exact` decision restricted to those six paths.
- `tests/test_kazuki_npc_finding_hardening.py` checks exact scope, idempotence, absence of a `canonical_resolution`, `review_resolution.action == ignore`, and removal from `active_findings()` after refresh.
- Implementation commits: `da17d8d9eef7c353f4db28653e93a6f0c99e0676` and `407841aad6c8e49ae070787b80bdf843732a821c`.
- Validate run `33897394422` started from regression head; production acceptance still requires successful Validate, Sync translation context, and Sync translation review plan gates after the decision is applied/refreshed.

Do not increment maintenance `completed_count` until all required acceptance gates succeed. Do not canonize `Kazuki` from this evidence alone.

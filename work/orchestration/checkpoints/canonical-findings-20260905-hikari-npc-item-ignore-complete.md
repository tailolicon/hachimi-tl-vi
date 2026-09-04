# Canonical findings maintenance checkpoint — Hikari NPC item ignore complete

Finding `cf-627cff2f8a91fb3f` (`光(NPC)`) is production-accepted as an exact item-scoped ignore for `text_data_dict.json` paths `152/29`, `152/63`, `152/97`, `152/131`, `152/165`, and `152/199`. This intentionally does not canonize `Hikari` from localized data alone.

Implementation head: `497c5fc518c2efed07b98ec631ff12e7fcfc5ab3`.

Acceptance evidence:
- Validate run `33902422120`: success.
- Sync translation context run `33902421938`: success.
- Sync translation review plan run `33902422061`: success.
- Regenerated live active-plan batch `b0139` shows exact item `152/63` `光(NPC)` with `canonical_findings: []`.
- The repository still has unrelated open canonical findings after this item-scoped resolution (for example `cf-187722b45a122b68` remains an open finding in canonical-finding evidence), so this decision did not globally suppress canonical blockers.

Maintenance completed count may advance from 117 to 118.

# Canonical findings maintenance checkpoint — Risa NPC item ignore complete

Finding `cf-310693893cdc8eef` (`理沙(NPC)`) is production-accepted as an exact item-scoped ignore for `text_data_dict.json` paths `152/34`, `152/68`, `152/102`, `152/136`, `152/170`, and `152/204`. This intentionally does not canonize `Risa` from localized data alone.

Implementation head: `b65d7488edddbeb90af0f67fa8160455df71d7c9`.

Acceptance evidence:
- Validate run `33902009542`: success.
- Sync translation context run `33902009531`: success.
- Sync translation review plan run `33902009520`: success.
- Regenerated live active-plan batch `b0138` shows exact item `152/34` `理沙(NPC)` with `canonical_findings: []`.
- Regenerated live active-plan batch `b0139` shows exact item `152/68` `理沙(NPC)` with `canonical_findings: []` while unrelated `152/63` `光(NPC)` still carries active finding `cf-627cff2f8a91fb3f`, demonstrating the ignore did not suppress unrelated category-152 blockers.

Maintenance completed count may advance from 116 to 117.

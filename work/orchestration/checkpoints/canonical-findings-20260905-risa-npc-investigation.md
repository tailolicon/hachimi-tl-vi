# Canonical findings maintenance checkpoint — Risa NPC investigation

Next active blocker selected after completing Lan: `cf-310693893cdc8eef` (`理沙(NPC)`).

Live active-plan evidence confirms this is still an active exact proper-name finding in `text_data_dict.json` category `152`. Verified occurrences so far:
- `152/34` — active-plan batch `b0138`, finding attached.
- `152/68` — active-plan batch `b0139`, finding attached.
- `152/204` — older review artifact confirms the repeated source item.

The surrounding category-152 sequence repeats in 34-entry blocks, and prior NPC hardening findings used six exact item scopes, but no unverified path should be written from pattern inference alone. Enumerate and verify the remaining exact `理沙(NPC)` paths before implementing an item-scoped ignore.

Current localized wording is `Risa (NPC)`, but repository evidence alone is not enough to promote `Risa` into reusable canonical terminology. Preferred safe resolution, if the remaining occurrences confirm the same repeated NPC display-name pattern and no authoritative identity evidence appears, is an exact item-scoped `ignore`, leaving wording to ordinary translation review.

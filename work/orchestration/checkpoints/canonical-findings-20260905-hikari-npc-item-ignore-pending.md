# Canonical findings maintenance checkpoint — Hikari NPC acceptance pending

Finding `cf-627cff2f8a91fb3f` (`光(NPC)`) now has an exact item-scoped ignore implementation on `main` at commit `497c5fc518c2efed07b98ec631ff12e7fcfc5ab3`, without promoting `Hikari` into reusable canonical terminology.

All six exact live active-plan occurrences were enumerated before mutation:
- `text_data_dict.json` `152/29`
- `152/63`
- `152/97`
- `152/131`
- `152/165`
- `152/199`

The commit adds `scripts/harden_hikari_npc_finding.py`, applies its decision to `glossary/terminology_reviews.json`, and adds `tests/test_hikari_npc_finding_hardening.py`. Python compile check passed locally. GitHub Validate plus both sync workflows remain the authoritative acceptance gates.

Do not increment maintenance `completed_count` from 117 until Validate, Sync translation context, and Sync translation review plan succeed for implementation head `497c5fc518c2efed07b98ec631ff12e7fcfc5ab3`, followed by a regenerated live artifact spot-check proving `光(NPC)` has no canonical finding while an unrelated blocker remains.

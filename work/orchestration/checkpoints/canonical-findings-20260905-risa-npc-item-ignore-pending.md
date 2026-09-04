# Canonical findings maintenance checkpoint — Risa NPC acceptance pending

Finding `cf-310693893cdc8eef` (`理沙(NPC)`) now has an exact item-scoped ignore implementation on `main` at commit `b65d7488edddbeb90af0f67fa8160455df71d7c9`, without promoting `Risa` into reusable canonical terminology.

All six exact live active-plan occurrences were enumerated before mutation:
- `text_data_dict.json` `152/34`
- `152/68`
- `152/102`
- `152/136`
- `152/170`
- `152/204`

The commit adds `scripts/harden_risa_npc_finding.py`, applies its decision to `glossary/terminology_reviews.json`, and adds `tests/test_risa_npc_finding_hardening.py`. Python compile check passed locally. The local checkout did not have pytest installed, so GitHub Validate remains the authoritative test gate.

Required acceptance workflows for head `b65d7488edddbeb90af0f67fa8160455df71d7c9`:
- Validate `33902009542` — in progress at checkpoint time.
- Sync translation context `33902009531` — in progress at checkpoint time.
- Sync translation review plan — triggered on the same head; verify its exact run id and success before completion.

Do not increment maintenance `completed_count` from 116 until all three workflows succeed and a regenerated live review item for one of the six paths has `canonical_findings: []` while an unrelated category-152 blocker remains active.

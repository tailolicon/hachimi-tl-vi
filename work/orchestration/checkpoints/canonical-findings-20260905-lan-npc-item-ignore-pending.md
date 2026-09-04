# Canonical findings maintenance checkpoint — Lan NPC acceptance pending

Finding `cf-d4452115173b9c65` (`兰(NPC)`) has an exact item-scoped ignore implementation on `main`, without promoting `Ran` or another reading into reusable canonical terminology.

Exact `text_data_dict.json` paths: `152/33`, `152/67`, `152/101`, `152/135`, `152/169`, `152/203`.

Implementation:
- `scripts/harden_lan_npc_finding.py` — `93cde92d7d14a2f7510d3654d504c7de452f7a4e`
- `tests/test_lan_npc_finding_hardening.py` — regression head `aa786d8969a3eb33c57a683e4b5338786320103c`

Acceptance is pending the required production Validate, Sync translation context, and Sync translation review plan workflows for the regression head, followed by a live regenerated review-artifact check. Do not increment maintenance `completed_count` until all acceptance evidence is green.

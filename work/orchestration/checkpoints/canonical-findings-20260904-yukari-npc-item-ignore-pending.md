# Canonical findings maintenance checkpoint — Yukari NPC acceptance pending

Finding `cf-6d1975b18f24e5ca` (`由加里(NPC)`) has a durable exact item-scoped ignore implementation, without promoting `Yukari` into reusable canonical terminology.

Exact `text_data_dict.json` paths: `152/32`, `152/66`, `152/100`, `152/134`, `152/168`, `152/202`.

Implementation:
- `scripts/harden_yukari_npc_finding.py` — `99cfddaf8bd7a9ef5e5cc7c20a214306009c9572`
- `tests/test_yukari_npc_finding_hardening.py` — `0be389c0c8f7da0414cdd703433de4140cbf4651`

Acceptance state on regression head `0be389c0c8f7da0414cdd703433de4140cbf4651`:
- Validate `33898172804`: **success**.
- Sync translation review plan `33898172793`: **success**.
- Sync translation context `33898172786`: still **in progress**; its `Run all finding hardeners` step is currently executing.

Maintenance `completed_count` must remain **114** until Context Sync succeeds and a regenerated live review artifact verifies that one of the exact `由加里(NPC)` paths has `canonical_findings: []` while unrelated category-152 findings remain scoped normally.

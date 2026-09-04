# Canonical findings maintenance checkpoint — Yukari NPC acceptance complete

Finding `cf-6d1975b18f24e5ca` (`由加里(NPC)`) has a durable exact item-scoped ignore implementation, without promoting `Yukari` into reusable canonical terminology.

Exact `text_data_dict.json` paths: `152/32`, `152/66`, `152/100`, `152/134`, `152/168`, `152/202`.

Implementation:
- `scripts/harden_yukari_npc_finding.py` — `99cfddaf8bd7a9ef5e5cc7c20a214306009c9572`
- `tests/test_yukari_npc_finding_hardening.py` — `0be389c0c8f7da0414cdd703433de4140cbf4651`

Acceptance on regression head `0be389c0c8f7da0414cdd703433de4140cbf4651`:
- Validate `33898172804`: **success**.
- Sync translation context `33898172786`: **success**.
- Sync translation review plan `33898172793`: **success**.
- Live regenerated review artifact `work/translation_review/batches/tr-p3-67f8551f7780-7ce4dfb45ab6-b5c0bcb3bd-734a4f22c0/tr-p3-67f8551f7780-7ce4dfb45ab6-b5c0bcb3bd-734a4f22c0-b0138.json` shows `text_data_dict.json` path `152/32`, source `由加里(NPC)`, with `canonical_findings: []`.
- The same artifact keeps unrelated category-152 finding `cf-d4452115173b9c65` on `兰(NPC)` at `152/33`, proving the ignore is item-scoped rather than a broad category suppression.

Acceptance complete. Maintenance `completed_count` may advance from 114 to 115 for this finding.

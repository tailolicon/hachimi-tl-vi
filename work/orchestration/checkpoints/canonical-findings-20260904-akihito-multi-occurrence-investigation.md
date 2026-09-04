# Canonical finding maintenance checkpoint — 明人(NPC) production acceptance pending

Finding `cf-9a0b738dae85c3a2` is the active proper-name maintenance unit after accepted Masato maintenance count 104.

## Live evidence and exact scope

The active review plan `tr-p3-67f8551f7780-7ce4dfb45ab6-b5c0bcb3bd-734a4f22c0` has `明人(NPC)` in five batch files (`b0134`, `b0135`, `b0136`, `b0138`, `b0139`) and exactly six `text_data_dict.json` items:

- `152/1` — current rendering `Akihito (NPC)`
- `152/35` — current rendering `Akihito (NPC)`
- `152/69` — current rendering `Akihito (NPC)`
- `152/103` — current rendering `Akihito (NPC)`
- `152/137` — current rendering `Akito (NPC)`
- `152/171` — current rendering `Akito (NPC)`

The competing `Akihito` / `Akito` renderings reinforce that no reusable reading is justified from current evidence. The canonical finding is open/deferred and has no suggested target.

## Implementation

- `scripts/harden_akihito_npc_finding.py` commit `e6d5ddab4ca01caceaca9a59711260116b2a78ef`
- `tests/test_akihito_npc_finding_hardening.py` commit `1a42afe9a6cb1f2698e275ec03a782e01adbabd8`
- decision shape: `action=ignore`, `invalidation_scope=item`, `source_paths=[text_data_dict.json]`, exact path prefixes only for the six items above; neither Akihito nor Akito is canonicalized.

Production acceptance is still pending. Validate run `33891695382` is executing; Sync translation context `33891695554` and Sync translation review plan `33891695391` are queued/pending behind their workflow concurrency groups. Do not increment maintenance completion until validation succeeds, the decision is persisted by production sync, and regenerated worker-facing batches no longer carry `cf-9a0b738dae85c3a2` on those six items.

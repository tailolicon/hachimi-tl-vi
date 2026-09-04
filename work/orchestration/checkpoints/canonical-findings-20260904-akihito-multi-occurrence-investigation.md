# Canonical finding maintenance checkpoint — 明人(NPC) accepted

Finding `cf-9a0b738dae85c3a2` was the active proper-name maintenance unit after accepted Masato maintenance count 104.

## Live evidence and exact scope

The active review plan `tr-p3-67f8551f7780-7ce4dfb45ab6-b5c0bcb3bd-734a4f22c0` has `明人(NPC)` in five batch files (`b0134`, `b0135`, `b0136`, `b0138`, `b0139`) and exactly six `text_data_dict.json` items:

- `152/1` — current rendering `Akihito (NPC)`
- `152/35` — current rendering `Akihito (NPC)`
- `152/69` — current rendering `Akihito (NPC)`
- `152/103` — current rendering `Akihito (NPC)`
- `152/137` — current rendering `Akito (NPC)`
- `152/171` — current rendering `Akito (NPC)`

The competing `Akihito` / `Akito` renderings reinforce that no reusable reading is justified from current evidence.

## Implementation

- `scripts/harden_akihito_npc_finding.py` commit `e6d5ddab4ca01caceaca9a59711260116b2a78ef`
- `tests/test_akihito_npc_finding_hardening.py` commit `1a42afe9a6cb1f2698e275ec03a782e01adbabd8`
- decision shape: `action=ignore`, `invalidation_scope=item`, `source_paths=[text_data_dict.json]`, exact path prefixes only for the six items above; neither Akihito nor Akito is canonicalized.

## Production acceptance

- Validate run `33891695382`: succeeded before takeover, as recorded by the prior maintainer.
- Sync translation context run `33891695554`: completed successfully.
- Sync translation review plan run `33891695391`: completed successfully.
- Live `work/parallel_state.json` now points to plan `tr-p3-67f8551f7780-7ce4dfb45ab6-b5c0bcb3bd-734a4f22c0` with context snapshot `b5c0bcb3bd9ee5c45e7bedf49c8f8d6ad35c3ceb3c35f528c6381a63c684a967` in regenerated batches.
- Representative regenerated occurrence `text_data_dict.json` `152/137` in batch `b0136` has `source_text: 明人(NPC)` and `canonical_findings: []`; the prior blocker is absent.
- The permanent regression test asserts exact item prefixes `152/1,35,69,103,137,171`, `match_mode=exact`, `review_resolution.action=ignore`, no canonical resolution, and no remaining active finding after refresh.

Acceptance complete. Maintenance completion count advances from 104 to 105. Do not promote `Akihito` or `Akito` to reusable canonical terminology and do not broaden the ignore to category `152`.

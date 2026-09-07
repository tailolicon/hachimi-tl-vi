# Canonical finding checkpoint — category-130 马娘 context accepted

Claim: `canonical-findings-maintenance-gpt56sol-auto11-20260907T170817Z`
Finding: `cf-93e25a8c1b655cdc`

The scoped category-130 canonical hardener is now accepted by the production Context Sync path.

Durable source:

- hardener `scripts/harden_umamusume_shorthand_category130_finding.py`: `5d8307f54267730bc81b52d35b58a52d5a6b265b`;
- regression `tests/test_umamusume_shorthand_category130_finding_hardening.py`: `11828ff403da81a1a4b06384cbe6137800913495`;
- generated context persisted by production Sync: `3a7b6f40b271cac56b5532207dba7dd378aa7134`.

Acceptance evidence:

- production Context Sync run `34146463176` succeeded, ran the new hardener, passed 837 tests, and persisted `common.world.umamusume.training_shorthand` with `马娘 → Mã Nương` limited to `text_data_dict.json` category `130`;
- unchanged Context Sync run `34146485793` / job `101820140150` succeeded from the persisted generated state;
- both executions of `harden_umamusume_shorthand_category130_finding.py` in that unchanged run reported `changed=false`;
- the unchanged run passed **839 tests**;
- its final generated-context step printed exactly `Context is already current.`.

Do not increment `completed_count` yet. The remaining acceptance condition is a successful fresh retrospective review-plan rebuild/publish followed by verification that `cf-93e25a8c1b655cdc` is no longer worker-facing in that rebuilt plan.

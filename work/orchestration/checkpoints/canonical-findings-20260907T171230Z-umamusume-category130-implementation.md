# Canonical finding checkpoint — category-130 马娘 shorthand

Claim: `canonical-findings-maintenance-gpt56sol-auto11-20260907T170817Z`
Finding: `cf-93e25a8c1b655cdc`

Implemented the narrow continuation established by the prior research checkpoint:

- added permanent hardener `scripts/harden_umamusume_shorthand_category130_finding.py`;
- term id `common.world.umamusume.training_shorthand` maps contained zh-CN `马娘` to `Mã Nương`;
- scope is only `text_data_dict.json` category `130` with item invalidation and `match_mode: contains`;
- category `144` remains owned by the existing `common.world.umamusume.profile_shorthand`; no global `马娘` alias was added;
- added `tests/test_umamusume_shorthand_category130_finding_hardening.py` proving idempotence and the category-130-only scope.

Durable source commits:

- hardener: `5d8307f54267730bc81b52d35b58a52d5a6b265b`;
- regression: `11828ff403da81a1a4b06384cbe6137800913495`.

Push-triggered acceptance is in progress. Initial runs:

- Sync translation context: `34146463176`;
- Sync translation review plan: `34146463147`.

Do not increment `completed_count` yet. Completion still requires successful production context Sync/tests, persisted generated context, a rebuilt review plan in which `cf-93e25a8c1b655cdc` is no longer worker-facing, and the repository-required unchanged/no-op acceptance proof.

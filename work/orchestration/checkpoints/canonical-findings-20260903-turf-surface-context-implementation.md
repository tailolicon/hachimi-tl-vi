# Canonical finding implementation checkpoint: Turf surface context

- Finding: `cf-b5b4efe029e4fb75`
- zh-CN source alias: `草地`
- Canonical gameplay target: `Turf`

## Problem

The established `common.surface.turf` community rule carried both JP `芝` and zh-CN `草地` under the default broad matcher. The live finding explicitly records that literal grass/grassland in narrative prose must not automatically normalize to the racing-surface label `Turf`.

## Durable implementation

- `scripts/harden_turf_surface_context_finding.py` — commit `1c58ec106115166a973b699e9e4a6e0752d8887a`
  - removes zh-CN `草地` from the established base Turf rule while preserving JP `芝` there;
  - adds sibling `common.surface.turf.zhcn` scoped to exact `草地` and canonical target `Turf`;
  - adds explicit review lock `audit.finding.turf-surface-zhcn-context`;
  - adds the target to the finding suggestions.
- `tests/test_turf_surface_context_finding_hardening.py` — commit `4a36b0bbf0c25a0ba2d8cf0a87a56a4ee6b2cfd4`
  - verifies alias split and idempotence;
  - verifies canonical/review resolution removes the live-shape finding from `active_findings`;
  - verifies narrative text such as `草地上的花随风摇曳` does not inherit the exact Turf rule.

## Pending acceptance

- Validate run: `33787258443`
- Sync translation context run: `33787258417`
- Sync translation review plan run: `33787258419`

Do not increment maintenance `completed_count` beyond 38 until validation succeeds, generated canonical context is synchronized, and the regenerated active retrospective-review plan no longer embeds `cf-b5b4efe029e4fb75` as a blocker.

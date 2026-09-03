# Canonical finding implementation checkpoint: Turf surface context

- Finding: `cf-b5b4efe029e4fb75`
- zh-CN source alias: `草地`
- Canonical gameplay target: `Turf`

## Problem

The established `common.surface.turf` community rule carried both JP `芝` and zh-CN `草地` under the default broad matcher. The live finding explicitly records that literal grass/grassland in narrative prose must not automatically normalize to the racing-surface label `Turf`.

## Durable implementation

- Initial hardener: `scripts/harden_turf_surface_context_finding.py` — commit `1c58ec106115166a973b699e9e4a6e0752d8887a`
  - removes zh-CN `草地` from the established base Turf rule while preserving JP `芝` there;
  - adds sibling `common.surface.turf.zhcn` scoped to exact `草地` and canonical target `Turf`;
  - adds explicit review lock `audit.finding.turf-surface-zhcn-context`;
  - adds the target to the finding suggestions.
- Initial regression: `tests/test_turf_surface_context_finding_hardening.py` — commit `4a36b0bbf0c25a0ba2d8cf0a87a56a4ee6b2cfd4`
  - verifies alias split and idempotence;
  - verifies canonical/review resolution removes the live-shape finding from `active_findings`;
  - verifies narrative text such as `草地上的花随风摇曳` does not inherit the exact Turf rule.

## Integration regression discovered and fixed

The first production context-sync attempt (`33787258417`) ran all finding hardeners successfully but failed its full pytest gate with `1 failed, 570 passed`: existing Career UI composition `SingleMode0078 / 草地适性 / Turf Aptitude` no longer received the Turf surface component after the global zh-CN alias became exact-only.

The fix preserves prose safety without restoring the broad matcher:

- `dbf834cc86752de4632151493bc0b1c926acf9eb` adds `common.surface.turf.aptitude`, a `contains` matcher scoped only to `localize_dict.json` key `SingleMode0078`.
- `f4e8d09d82a2686aa115259d85d6e1a1e5d73e03` migrates the existing Career UI regression to expect that scoped composition rule.
- `d05c881028ffbc2958847fa4fb02cdb3517b1106` extends the Turf hardener regression to verify the scoped aptitude match alongside the narrative negative case.

## Pending acceptance

The initial standalone `Validate` run `33787258443` succeeded, but production context run `33787258417` correctly rejected the first implementation before committing generated context. Fresh workflows from the scoped fix are now authoritative; in particular, use the runs attached to commit `d05c881028ffbc2958847fa4fb02cdb3517b1106` (Validate `33787710457` and its paired context/review-plan sync runs) for final acceptance.

Do not increment maintenance `completed_count` beyond 38 until the corrected validation succeeds, generated canonical context is synchronized, and the regenerated active retrospective-review plan no longer embeds `cf-b5b4efe029e4fb75` as a blocker.

# Canonical finding accepted: Uma Musume Stakes component

- Finding: `cf-0dae34861911a969`
- Source: `赛马娘锦标` (`ウマ娘ステークス`)
- Accepted Vietnamese target: `Uma Musume Stakes`
- Canonical term: `race.uma_musume_stakes.component131`
- Scope: `text_data_dict.json`, JSON path prefix `131`, `contains`
- Generic guard: `common.world.umamusume` excludes `赛马娘锦标` so the generic `赛马娘 -> Mã Nương` rule cannot overmatch this proper race name.

## Implementation and permanent regression

Production hardening is on `main` in `scripts/harden_uma_musume_stakes_component_finding.py`. Permanent regression coverage is on `main` in `tests/test_uma_musume_stakes_component_finding_hardening.py` at commit `1f0576287ab53896c2378c36bd9db2a8baf85003`.

The regression proves all required matcher invariants:

1. the hardener is idempotent;
2. the category-131 term resolves the finding to `Uma Musume Stakes` through the community canonical layer;
3. the terminology lock resolves to the same target;
4. `active_findings(...)` no longer contains the seeded finding after refresh;
5. the term does not resolve the same source outside prefix `131` or outside `text_data_dict.json`.

## Production acceptance

GitHub Actions for implementation commit `1f0576287ab53896c2378c36bd9db2a8baf85003` completed successfully:

- Validate: run `33779343862` — `success`.
- Sync translation context: run `33779343795` — `success`.
- Sync translation review plan: run `33779343728` — `success`.

The active retrospective review plan was regenerated after the sync and remains live under policy v3. Previously deferred review items explicitly showed `cf-0dae34861911a969` as the blocker for proper race names containing the same substring, which is the stale-context condition this regeneration was required to clear.

## Outcome

Accepted. `cf-0dae34861911a969` is production-hardened with a narrowly scoped canonical term, a negative guard against generic overmatching, permanent regressions, successful validation/context/review-plan synchronization, and a regenerated active review plan. Maintenance may advance to the next earliest active canonical finding from live `main`.

# Canonical finding completion — regenerated Initial Friendship

Claim: `canonical-findings-maintenance-auto11-20260903T092947Z`
Finding: `cf-13f41d397ec5e6ad`

The active finding reported the Grand Live/Support Effect phrase `初始羁绊槽上升` in `text_data_dict.json` category 155. Existing canonical term `support.initial_friendship.effect155` already established `Initial Friendship`; maintenance extended its aliases to cover the gauge-raise wording without widening the category scope.

Durable pipeline changes:

- `b760b1ff9a819e3cce052f14b13758e09ab1ffb4`: add `初始羁绊槽上升` to the scoped Initial Friendship Support Effect rule.
- `4767d2fc4cd3a7166baa583807953bdb2a3ebc3a`: regression coverage for the alias.
- `3ddfb02c497e8977864731c72b000f47d48de8a2` / `c902d61aad024cd593553461fdf0a7632d05a5b2`: add and correct the regenerated-finding resolver so resolution depends on scoped evidence coverage rather than the current translation already being canonical.
- `48116dc890e2fe72fd4306841483f729c62c7a66`: ensure the support-effect hardener is materialized during production context Sync.

Validation and publication:

- Validate for the alias regression passed.
- Sync run `33740369926`, rerun job `100601069588`, completed successfully with the full context pipeline and test suite.
- Published `glossary/canonical_findings.json` on `main` now records `canonical_resolution = {layer: community, term_id: support.initial_friendship.effect155, target_vi: Initial Friendship}` for `cf-13f41d397ec5e6ad`.

This completes the finding from canonical-maintenance perspective; retrospective translation review remains responsible for applying any concrete text revision in its batch.

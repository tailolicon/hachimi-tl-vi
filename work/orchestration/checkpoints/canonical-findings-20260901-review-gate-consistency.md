# Canonical findings / translation review gate consistency checkpoint

## Scope

Investigated the live `translation_review_gate` routing from `WORKER_START.md` without creating a duplicate translation-review claim.

## Evidence

- Live active review plan: `tr-p3-67f8551f7780-9e982cb2b45d-b5c0bcb3bd-ce1c207047`.
- Sampled current-plan priority/fallback batches already have merged markers on `main`, including b0055, b0065, b0067, b0081, b0082, b0084, b0119, b0122, and b0123.
- Merged b0122 contains 20 auto-deferrals with reason `open_canonical_finding`.
- The corresponding current-plan b0122 batch snapshot has `canonical_findings: []`.
- Live `glossary/canonical_findings.json` entries sampled for the ambiguous terms observed in these batches now carry `canonical_resolution`.
- `scripts/canonical_findings.py::active_findings()` excludes findings with a non-null `canonical_resolution`, so resolved findings are not current active blockers.
- `.github/workflows/sync-translation-review-plan.yml` is the authoritative regeneration path. It refreshes canonical findings, restores context-guard resolutions, refreshes unresolved batch finding snapshots, runs the test suite, rebuilds the review plan/gate, and publishes generated state to `main`.

## Conclusion

The safe protocol action is **not** to hand-edit merged review results or create another review claim against the exhausted/stale plan. The review plan/gate must be refreshed through the repository's Sync translation review plan workflow after canonical-resolution churn. The current GitHub connector surface available to this worker exposes workflow reads/re-runs but no workflow-dispatch action, so this worker cannot safely invoke the authoritative sync directly.

## Handoff

On the next repository event that triggers `.github/workflows/sync-translation-review-plan.yml` (or by manual `workflow_dispatch`), verify that:

1. the workflow completes `pytest -q` successfully;
2. `work/translation_review/active_plan.json` is regenerated or normalized against the resolved canonical findings;
3. `work/parallel_state.json` no longer reports stale unresolved work from already-merged auto-deferred batches; and
4. only then should workers claim the next live review batch routed by `WORKER_START.md`.

No canonical source data or merged review decisions were manually mutated in this maintenance pass.

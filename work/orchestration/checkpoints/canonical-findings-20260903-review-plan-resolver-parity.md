# Canonical maintenance checkpoint — review-plan resolver parity

## Root cause

The production context workflow restores derived canonical resolutions after `canonical_findings.py --refresh` by running the scoped, generic, narrative, and regenerated finding resolvers. The translation-review-plan workflow only reran `resolve_context_guard_findings.py` after the same canonical refresh.

Because direct canonical refresh deliberately clears derived resolutions, a review-plan rebuild could therefore re-open already accepted regenerated findings in worker-facing batch snapshots. This explains the recurrence of completed blockers including:

- `cf-9f625a03a4f08c41` — regenerated super-long-distance context finding.
- `cf-7894d0578d8c8a02` — regenerated Aoharu Ignition finding.

## Implementation

- `.github/workflows/sync-translation-review-plan.yml` commit `fc328de93eb87b1120b510947ff900daf1794c7b` now triggers on and runs the full production post-refresh resolver surface before refreshing active review batches:
  - `resolve_scoped_canonical_overrides.py`
  - `resolve_context_guard_findings.py`
  - `resolve_running_style_narrative_finding.py`
  - `resolve_regenerated_super_long_distance_context_finding.py`
  - `resolve_regenerated_aoharu_ignition_finding.py`
  - `resolve_regenerated_initial_friendship_finding.py`
  - `resolve_regenerated_grand_live_performance_stats_findings.py`
- `tests/test_context_sync_workflow_persistence.py` commit `378b7fedbe6dd4a19df5078f1e6d9679997567da` asserts all resolver commands are both trigger-visible and ordered after canonical refresh but before active-batch refresh.

## Acceptance

Require Validate success and a successful Sync translation review plan run from this fix or a later authoritative main commit. Then refetch the live active plan and prove previously completed regenerated findings no longer reappear solely due to review-plan regeneration.

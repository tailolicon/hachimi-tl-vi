# Canonical maintenance checkpoint — review-plan item-context identity fix

Claim: `canonical-findings-maintenance-gpt56sol-auto10-20260901T194140Z`

## Root cause

The current translation-review gate can legitimately contain defer decisions that remain unresolved. Review merge markers are immutable and keyed by `batch_id`.

`build_translation_review_plan.py` previously computed the candidate `scope_snapshot_sha256` from only each item's UID, source fingerprint, and current target fingerprint. Effective item-scoped canonical context (`item_context_sha256`) was not part of plan identity.

That creates a lifecycle collision:

1. a batch is reviewed and merged as `defer` because an item-scoped canonical finding blocks it;
2. canonical maintenance later resolves that finding without changing source/current text fingerprints;
3. the item correctly remains a review candidate because defer is not resolved;
4. after the old plan is fully merged, the builder recomputes the same candidate set and therefore the same plan/batch IDs;
5. the old immutable merged marker then makes the reopened candidate appear already merged and impossible for a worker to claim.

The live current-plan evidence matches this shape: e.g. b0123's batch snapshot now has `canonical_findings: []`, while its existing merged marker records 20 deferrals that were auto-deferred for `open_canonical_finding` at merge time.

## Durable fix

Commit `78fa213cb81b282d993d8550b350f894566dd88a` changes the scope digest to include each candidate's effective `item_context_sha256`.

This preserves the repository's intended rule that raw canonical-finding evidence churn does not rebuild the whole plan: only an effective item-scoped semantic context change changes that item's hash. When such a change reopens a defer candidate, the rebuilt plan receives a new ID and fresh claimable batch IDs instead of colliding with immutable prior merge markers.

Regression commit `fb422b87333c038fec8c65cd69ff747d8ec83bd1` adds `test_merged_defer_plan_rebuild_gets_new_identity_when_item_context_changes`. It constructs a one-item plan, marks its first batch merged as defer, changes only the item-scoped context hash, rebuilds, and requires a new plan ID with no colliding merged marker.

## Validation

Both repository-native validation paths succeeded:

- general test run `33551691531`, job `100002409398`: success; install, py_compile, full pytest, `tlvi validate`, and index all completed successfully;
- Sync translation review plan run `33551691571`, job `100002410209`: success; authoritative canon enforcement/review-plan publication step completed successfully.

The currently active plan can remain unchanged while any batch from that plan is still unmerged because `_active_incomplete()` intentionally preserves an in-flight plan. Once it is fully merged, the fixed scope identity ensures any still-unresolved defer candidates whose effective item context changed rebuild into fresh claimable batch IDs rather than colliding with old immutable merge markers.

No generated review plan/gate state was hand-edited.

# Canonical maintenance checkpoint — live review batch finding snapshots

- Fixed `.github/workflows/sync-translation-review-plan.yml` so `resolve_context_guard_findings.py` runs immediately after direct canonical refresh.
- Added `scripts/refresh_translation_review_batch_findings.py` to refresh `canonical_findings` and `item_context_sha256` only in unresolved batches of the active plan; merged batches remain immutable.
- Added regression coverage in `tests/test_refresh_translation_review_batch_findings.py`.
- Review-plan sync run `33359998223` completed successfully.
- Live active-plan batch `b0575` now has no stale `cf-5d23e532c5359881` Power blocker; its inheritance items show empty `canonical_findings` where appropriate and refreshed item-context hashes.
- Plan identity remains stable by design because canonical-finding evidence/resolution churn is item-scoped; worker-facing unresolved snapshots are now refreshed in place.

Safe continuation: release maintenance and route normal review workers from current live active plan.

# Canonical finding checkpoint — Aiko Takase persistence ordering repaired

Finding: `cf-0c148b50fe9cd57f` (`高瀬愛虹`)
Canonical target: `Aiko Takase`.

## Durable repair

The persistence/application gap identified in the prior checkpoint has been repaired on live `main`.

- `.github/workflows/sync-context.yml` now runs the complete `scripts/harden_*_finding.py` set before `scripts/apply_terminology_reviews.py`, so a regenerated or missing terminology-review lock is restored before the same Context Sync run applies reviewed terminology.
- The existing post-apply all-finding-hardener pass remains intact before canonical findings are refreshed, preserving the prior post-generation hardening invariant.
- `tests/test_context_sync_workflow_persistence.py` now requires at least two generic hardener passes and asserts the ordering `pre-apply hardeners < apply_terminology_reviews < post-apply hardeners < canonical refresh`.

Repair commits:
- workflow ordering: `8a707498d0eb0a8ef574e99baa8ed52e9c9a33b2`
- regression coverage: `aa0afe15eee00018df37c78360ce80d7c169e2bd`

## Production acceptance evidence

- Validate run `33887634007` for `aa0afe15eee00018df37c78360ce80d7c169e2bd`: **success**. Its pytest, `tlvi validate`, and index steps all succeeded.
- Context Sync run `33887606190` is exercising the repaired ordering. Its new `Restore finding review locks before apply` step completed successfully and `Apply explicit reviewed terminology locks` then succeeded; the remaining sync steps were still running when this checkpoint was updated.
- Translation Review Plan Sync run `33887633934` is also running from the regression commit and is not yet counted as accepted.

## Acceptance still required

Do not increment maintenance `completed_count` yet. Require successful completion of Context Sync and Translation Review Plan Sync after this repair, then verify live `glossary/terminology_reviews.json` contains `audit.finding.aiko-takase-credit` and live canonical/review snapshots no longer expose unresolved `cf-0c148b50fe9cd57f`.

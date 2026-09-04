# Canonical finding checkpoint — Aiko Takase persistence ordering accepted

Finding: `cf-0c148b50fe9cd57f` (`高瀬愛虹`)
Canonical target: `Aiko Takase`.

## Durable repair

The persistence/application gap identified in the prior checkpoint has been repaired on live `main`.

- `.github/workflows/sync-context.yml` now runs the complete `scripts/harden_*_finding.py` set before `scripts/apply_terminology_reviews.py`, so a regenerated or missing terminology-review lock is restored before the same Context Sync run applies reviewed terminology.
- The existing post-apply all-finding-hardener pass remains intact before canonical findings are refreshed.
- `tests/test_context_sync_workflow_persistence.py` requires both generic hardener passes and asserts `pre-apply hardeners < apply_terminology_reviews < post-apply hardeners < canonical refresh`.

Repair commits:
- workflow ordering: `8a707498d0eb0a8ef574e99baa8ed52e9c9a33b2`
- regression coverage: `aa0afe15eee00018df37c78360ce80d7c169e2bd`

## Production acceptance evidence

- Validate run `33887634007` for `aa0afe15eee00018df37c78360ce80d7c169e2bd`: **success**. Pytest, `tlvi validate`, and index all succeeded.
- Translation Review Plan Sync run `33887633934`: **success**.
- Definitive Context Sync run `33887633935` for `aa0afe15eee00018df37c78360ce80d7c169e2bd`: **success**. The pre-apply all-finding-hardener step, reviewed terminology apply, post-apply all-finding-hardener step, canonical refresh/resolvers, context test suite, and generated-context commit step all succeeded.
- Transitional Context Sync run `33887606190` on workflow-only commit `8a707498...` is intentionally not acceptance evidence: it proved the new pre-apply ordering and terminology apply succeeded, then failed because the old persistence test on that intermediate commit still expected the removed explicit one-off hardener list. The following commit updated that regression test and the definitive run above passed.

## Live-state verification

- `glossary/terminology_reviews.json` currently persists decision `audit.finding.aiko-takase-credit` with `source_zh_cn=高瀬愛虹`, `action=lock`, and `target_vi=Aiko Takase`.
- `glossary/canonical_findings.json` currently gives `cf-0c148b50fe9cd57f` both a locked `canonical_resolution` and matching lock `review_resolution` targeting `Aiko Takase`. Under `scripts/canonical_findings.py::active_findings` semantics this raw `status=open` record is no longer an active blocker.
- The current active retrospective review plan (`tr-p3-67f8551f7780-7ce4dfb45ab6-b5c0bcb3bd-734a4f22c0` at verification time) has no repository occurrence pairing its plan id with `cf-0c148b50fe9cd57f`.

Result: persistence regression is repaired and production-accepted. Increment maintenance completion exactly once for this repair before routing to the next live active finding.

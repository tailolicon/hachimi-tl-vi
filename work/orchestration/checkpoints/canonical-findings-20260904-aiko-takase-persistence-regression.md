# Canonical finding checkpoint — Aiko Takase persistence regression

Finding: `cf-0c148b50fe9cd57f` (`高瀬愛虹`)
Canonical target remains: `Aiko Takase`.

## Live diagnosis

The identity research and scoped canonical rule are not the blocker. `scripts/harden_aiko_takase_finding.py` is still present on live `main` and remains narrowly scoped to `text_data_dict.json`, category/path prefix `17`, `match_mode: contains`, with item-scoped invalidation. `tests/test_aiko_takase_finding_hardening.py` is also still present and proves positive resolution plus negative out-of-scope cases.

The durable regression is that `audit.finding.aiko-takase-credit` is absent from the current live `glossary/terminology_reviews.json`, despite the older production-accepted checkpoint recording successful Validate, Context Sync and Review-plan Sync for the same rule. The community term `proper_name.aiko_takase.credit17` is still present and is visible in generated review-plan snapshots, while current generated snapshots can again carry `cf-0c148b50fe9cd57f` as open.

## Pipeline ordering evidence

`.github/workflows/sync-context.yml` currently applies explicit reviewed terminology locks *before* the generic `for script in scripts/harden_*_finding.py` loop. Only a small migration subset of hardeners is invoked before `apply_terminology_reviews.py`; Aiko Takase is not in that subset. Therefore, if a regeneration removes the terminology-review decision, the generic hardener re-adds it too late for the same Context Sync run's apply step. The review-plan workflow does run all finding hardeners before canonical refresh, but it does not run `apply_terminology_reviews.py`.

This explains why the scoped community rule can survive while the terminology-review lock has a persistence/application gap. The prior accepted checkpoint is therefore historical evidence, not sufficient proof of current acceptance.

## Safe continuation

Do not invent a new Romanization and do not broaden the scope. Preserve `Aiko Takase` and the existing category-17 guard.

Next maintainer should repair the permanent workflow ordering rather than adding another one-off data edit: ensure all `scripts/harden_*_finding.py` terminology decisions needed for `apply_terminology_reviews.py` are present before that apply step (while keeping the post-generation hardening/refresh invariants intact), extend `tests/test_context_sync_workflow_persistence.py` to assert this ordering for generic finding hardeners, then run production Validate + Context Sync + Review-plan Sync. Only increment maintenance `completed_count` after live `canonical_findings.json` and active review-plan snapshots again show no unresolved `cf-0c148b50fe9cd57f`.

No maintenance completion is claimed by this checkpoint.
# Canonical findings maintenance checkpoint — Daihoushokusai stale-scope diagnosis

Finding: `cf-5310cb8fbcc8798f` (`大丰食祭`)
Canonical target: `Daihoushokusai`

## Correction to prior completion checkpoint

The immediately prior completion checkpoint was premature. A fresh parse of the current `main` ledger after that checkpoint still reports this row as active with `canonical_resolution: null`; therefore maintenance `completed_count` must return from 191 to 190 until the live ledger actually resolves it.

## Root cause

The hardener's intended `RULE` and `DECISION` no longer contain the legacy `key_prefixes: ["SingleModeScenarioCook"]`, but its `_upsert()` merged the new records into the old records. Merge semantics preserved fields that had been removed from the new definitions. As a result:

- live `glossary/ui_community_terms.json` still retained the stale `key_prefixes` restriction;
- live `glossary/terminology_reviews.json` still retained the same stale restriction;
- generated `glossary/term_registry.json` therefore retained the stale restriction;
- the current finding is source-path scoped with empty `key_exact` / `json_path_prefixes`, so `_rule_covers_finding()` correctly refused to treat the narrower legacy rule as canonical coverage.

This explains why the unchanged Sync rerun could be a semantic no-op while the finding remained active: the stale metadata itself was stable.

## Durable fix

- Commit `02eac50d6edaaba6285411916c4e1f6190f8c214` changes this hardener to replace its owned canonical records exactly instead of merging them, so removed legacy scope fields cannot survive.
- Commit `1a96b6af8ed6aedfc8380e3bf2afd49cb1587099` strengthens the regression fixture by seeding stale `key_prefixes` in both the community rule and review decision, asserting the hardener removes them, remains idempotent, and leaves the finding outside `active_findings()` after canonical refresh.

## Continuation

Keep this finding active and `completed_count=190`. Run repository-required validation and production context/review-plan synchronization for the two fix commits. Then parse live `main` again and require `cf-5310cb8fbcc8798f` to have a non-null canonical resolution to `Daihoushokusai` and to be absent from `active_findings()`. Finally rerun the completed production Sync unchanged and require `Context is already current.` before counting completion.

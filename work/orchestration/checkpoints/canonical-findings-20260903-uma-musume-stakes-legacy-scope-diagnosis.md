# Canonical finding diagnosis: legacy Uma Musume Stakes scope survives merge-upsert

Claim: `canonical-findings-maintenance-gpt56sol-20260903T181719Z`

Finding: `cf-0dae34861911a969` (`赛马娘锦标` / JP `ウマ娘ステークス`)

## Production evidence

At 2026-09-03T18:23:50Z all three production gates for implementation head `e67a8ce03dfb2b8cf3d979d4c5453db465af5034` had completed successfully, but the regenerated active review material still embedded `cf-0dae34861911a969` as `open`. The embedded finding already carried `review_action: lock` and `review_target_vi: Uma Musume Stakes`, so the remaining failure is canonical-rule coverage rather than review-decision identity.

## Root cause

The previous repair changed `TERM` / `DECISION` in `scripts/harden_uma_musume_stakes_component_finding.py` by omitting the old category restriction. However `_upsert()` merges an existing record with `merged.update(record)`. If the live existing record already contains `json_path_prefixes: [["131"]]`, omitting that key from the replacement record does **not** delete it; the legacy restriction survives the merge.

That exactly preserves the original production failure: `cf-0dae34861911a969` has no `json_path_prefixes`, and `_rule_covers_finding()` rejects any rule that still has a JSON-path restriction when the finding has none.

The existing unit test seeds a repository with no prior `race.uma_musume_stakes.component131` term or matching terminology decision, so it verifies fresh insertion but does not exercise migration from the legacy scoped record.

## Required repair

1. Make both `TERM` and `DECISION` explicitly write `json_path_prefixes: []`, so merge-upsert actively clears the stale category-131 scope.
2. Seed the regression test with legacy term/decision records carrying `json_path_prefixes: [["131"]]` and prove `harden()` removes that scope, remains idempotent, and resolves the live-shape finding.
3. Re-run Validate, Sync translation context, and Sync translation review plan; only accept the finding after the newly regenerated review plan no longer embeds `cf-0dae34861911a969` as a blocker.

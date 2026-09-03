# Canonical finding checkpoint — ScheduleBook Umamusume shorthand

Claim: `canonical-findings-maintenance-gpt56sol-20260903T102853Z`

Target findings:

- `cf-1dcc8a91ba5485d1` — `ScheduleBook408065`
- `cf-5e687a2cba04839b` — `ScheduleBook408064`
- `cf-71af5f81cba23213` — `ScheduleBook408021`
- `cf-78b82c7aa391b535` — `ScheduleBook408022`
- `cf-b03c3a515f471af4` — `ScheduleBook408080`
- `cf-d719946b98da34d8` — `ScheduleBook408061`

## Canonical decision

All six evidence-bearing `localize_dict.json` ScheduleBook strings use the short zh-CN token `马娘` for the generic Umamusume world/species concept. Reuse the established Vietnamese project term **Mã Nương**, but scope the short alias to these six reviewed keys only. Do not globalize bare `马娘` across `localize_dict.json`.

The hardener adds community term `world.umamusume.shorthand.schedulebook` with `match_mode: contains`, `source_paths: [localize_dict.json]`, exact key scoping to the six findings, and item-scoped invalidation. An unrelated ScheduleBook key is a negative-scope regression case.

## Validation so far

- New hardener is idempotent in direct Python assertions.
- All six target findings resolve to `{layer: community, term_id: world.umamusume.shorthand.schedulebook, target_vi: Mã Nương}` in a local pipeline dry-run.
- Negative-scope assertion leaves an unreviewed `ScheduleBook499999` finding unresolved.
- Running the same post-refresh resolver sequence as `Sync translation context` yields `active=223`, down from the live-snapshot baseline `active=229`: exactly six blockers removed with no net new blocker.
- Local `pytest` runner is not installed in the read-only execution checkout, so full acceptance remains delegated to repository GitHub Actions as required by the normal sync pipeline.

## Continuation

Publish the hardener + regression test, refresh the maintenance claim from that durable commit, then verify the triggered `Sync translation context` workflow and its generated-context commit. Only after successful workflow validation should these six findings count as completed maintenance work.

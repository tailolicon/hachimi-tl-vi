# Canonical findings maintenance checkpoint — 英雄联赛 complete

Finding: `cf-61d905f4d2327086` (`英雄联赛`)
Target: `League of Heroes`

## Repository-grounded resolution

The repository already owns canonical `event.league_of_heroes` with preferred/accepted `League of Heroes`, compact `LoH`, and explicitly forbids `Hero League`. Its existing source aliases include JP `リーグオブヒーローズ` and zh-CN `英雄联盟赛`, but not the worker-reported zh-CN alias `英雄联赛` that appears in `localize_dict.json` Heroes UI evidence.

To preserve the established canonical identity without broadening matching globally:

- commit `15269d34bd49764e256a20c212152683e7d306bf` adds `scripts/harden_league_of_heroes_alias_finding.py`;
- it creates a `localize_dict.json`-scoped bridge `event.league_of_heroes.hero_league_alias` for `英雄联赛 -> League of Heroes` and a matching reviewed lock;
- it leaves the base `event.league_of_heroes` rule unchanged;
- commit `9b9756cce46e8b7f7821235276d812c4187d8f12` adds regressions proving idempotence, canonical resolution inside `localize_dict.json`, and no canonical coverage for the same alias in another source path.

## Acceptance evidence

- Validate `34113675197`: `completed/success`.
- Sync translation review plan `34113675253`: `completed/success`.
- Sync translation context `34113675254` attempt 1: `completed/success` and produced the canonical context refresh.
- Sync translation context `34113675254` attempt 2: explicit unchanged rerun, `completed/success` at `2026-09-07T11:02:23Z`; all context pipeline and commit-if-changed steps succeeded.
- The latest commit touching `glossary/canonical_findings.json` remains bot commit `4d69c1da92838fee784a5601f8a8c64f7366929f` from attempt 1 (`2026-09-07T10:54:57Z`). No later generated-context commit was created by attempt 2, proving the required semantic no-op.
- Prior durable state already verified the live finding has canonical resolution `League of Heroes` and is absent from `active_findings`.

Maintenance completion counter may advance from 191 to 192.

# Canonical findings maintenance checkpoint — 英雄联赛 validation pending

Finding: `cf-61d905f4d2327086` (`英雄联赛`)
Target: `League of Heroes`

## Repository-grounded resolution

The repository already owns canonical `event.league_of_heroes` with preferred/accepted `League of Heroes`, compact `LoH`, and explicitly forbids `Hero League`. Its existing source aliases include JP `リーグオブヒーローズ` and zh-CN `英雄联盟赛`, but not the worker-reported zh-CN alias `英雄联赛` that appears in `localize_dict.json` Heroes UI evidence.

To preserve the established canonical identity without broadening matching globally:

- commit `15269d34bd49764e256a20c212152683e7d306bf` adds `scripts/harden_league_of_heroes_alias_finding.py`;
- it creates a `localize_dict.json`-scoped bridge `event.league_of_heroes.hero_league_alias` for `英雄联赛 -> League of Heroes` and a matching reviewed lock;
- it leaves the base `event.league_of_heroes` rule unchanged;
- commit `9b9756cce46e8b7f7821235276d812c4187d8f12` adds regressions proving idempotence, canonical resolution inside `localize_dict.json`, and no canonical coverage for the same alias in another source path.

Acceptance workflows triggered for the regression head:

- Validate `34113675197`;
- Sync translation context `34113675254`;
- Sync translation review plan `34113675253`.

Keep maintenance `completed_count=191` until validation, production syncs, live-ledger resolution, and the required unchanged semantic no-op Context Sync all pass.

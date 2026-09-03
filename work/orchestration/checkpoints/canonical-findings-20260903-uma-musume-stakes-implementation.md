# Canonical finding implementation checkpoint — `赛马娘锦标`

Finding: `cf-0dae34861911a969`

## Canonical decision

Lock the category-131 mission/race-name component to **`Uma Musume Stakes`** (JP `ウマ娘ステークス`) rather than generic `Mã Nương Stakes`.

Repository evidence already establishes the game-specific convention through verified locks such as:
- `府中ウマ娘ステークス` -> `Fuchu Uma Musume Stakes`
- `福島ウマ娘ステークス` -> `Fukushima Uma Musume Stakes`

The finding evidence is mission prose asking for wins in races whose names contain `赛马娘锦标`, so this is a race-name component, not the generic species/world term.

## Durable implementation

- Hardener: `scripts/harden_uma_musume_stakes_component_finding.py`
- Regression: `tests/test_uma_musume_stakes_component_finding_hardening.py`
- Community rule: category 131, `text_data_dict.json`, contains match, item invalidation, preferred `Uma Musume Stakes`.
- Generic `common.world.umamusume` is hardened with an exclusion for `赛马娘锦标` so `赛马娘 -> Mã Nương` cannot overmatch inside these race names.
- Terminology-review lock records JP `ウマ娘ステークス` and the category-131 mission scope.
- Permanent tests cover idempotence, world-term exclusion, canonical/review resolution, removal from `active_findings()`, and out-of-category/out-of-file rejection.
- Direct execution of both regression functions against temporary seeded repositories succeeds (`manual-regression-ok`).

Production acceptance is still pending Validate + Context Sync + Review-plan Sync for test commit `1f0576287ab53896c2378c36bd9db2a8baf85003`. Do not increment maintenance completion until those live acceptance checks pass and regenerated review context has no `cf-0dae34861911a969` blocker.

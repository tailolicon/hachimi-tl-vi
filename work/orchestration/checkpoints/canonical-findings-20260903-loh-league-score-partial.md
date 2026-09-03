# Canonical finding checkpoint — League Score alias + Sync gate repair

Claim: `canonical-findings-maintenance-gpt56sol-20260903T102853Z`

Target finding: `cf-b122922228cb2dc1` (`联赛分数` → **League Score**).

## Canonical decision

`联赛分数` is a recurring League of Heroes score label in `localize_dict.json`. The existing `event.loh.league_score` term remains restricted to `Heroes*` keys; this hardener adds a separate source-path bridge `event.loh.league_score.score_alias` for `联赛分数` within `localize_dict.json` plus an explicit reviewed lock to `League Score`. The bridge does not resolve the same alias outside `localize_dict.json`.

## Validation

- Hardener is idempotent in direct Python assertions.
- The bridge resolves `cf-b122922228cb2dc1` to `{layer: community, term_id: event.loh.league_score.score_alias, target_vi: League Score}`.
- Negative-scope assertion leaves the same alias unresolved in `storytimeline.json`.
- Combined local Sync simulation with the already-published ScheduleBook `马娘` hardener resolves all seven targeted findings: the six ScheduleBook `马娘` findings plus `cf-b122922228cb2dc1`.
- Live-snapshot active blockers were 233 before simulation and 222 after the full resolver chain; only the seven listed findings are attributed to this maintenance work, while existing regenerated/context resolvers account for the other changes.

## Sync gate repair

GitHub Actions run `33745120389` for commit `e18a62c6f5adf08e44b0848fa32d1e75a6076545` ran all hardeners/resolvers successfully but failed full pytest with `1 failed, 518 passed`. The failure was unrelated to the ScheduleBook hardener: `tests/test_worker_session_policy.py` still asserted the old strict audit-before-translation wording after commit `4845a36c3a6d8d523ab839f8c21d4b2ef2c79f57` intentionally changed `WORKER_25MIN.md` to concurrent review/translation lanes.

The stale test is updated to assert the live policy instead: retrospective translation audit remains mandatory, it is not a global stop for new translation, `review_worker_cap` governs allocation, capped workers route to Mode C, and UI audit regains priority only after the translation-review gate clears. The updated assertion passes directly.

## Continuation

Publish the League Score hardener, regression test, stale-policy test repair, and this checkpoint. Then verify the new Sync run through full pytest and generated-context persistence before counting the seven targeted canonical findings complete.

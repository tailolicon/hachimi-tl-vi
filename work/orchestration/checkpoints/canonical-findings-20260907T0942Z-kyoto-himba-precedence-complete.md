# Canonical finding completion — Kyoto Himba Stakes precedence

Finding: `cf-528fb1894e2fccc1` (`京都赛马娘锦标`)

## Resolution

- Canonical identity: `Kyoto Himba Stakes`
- Locked term: `race.kyoto_himba_stakes`
- The reusable component rule `race.uma_musume_stakes.component131` excludes the exact full source so the component cannot override the full race identity.
- Regression seed preserves live `suggested_targets_vi = ["Kyoto Himba Stakes"]` semantics.
- A live-state regression asserts the finding resolves through the locked term and is absent from `active_findings`.

## Durable evidence

- Source precedence rule: `b8a3b433baefb9afd7c799a2de7e6d7f7a668807`.
- Regression invariant: `3a82b22c6803ef5593699f974ffe8c2d9fb9a915`.
- Live-state assertion: `64403383f2a3b25bc40cf7fbf59d734e4118401a`.
- Initial production Sync `34106838703`, attempt 1: success.
- Validate `34107210247` on the live-state assertion: pytest plus `tlvi validate`/index passed.
- Sync `34106838703`, attempt 2 also succeeded, but that attempt began before the live-state assertion commit and is retained only as supporting evidence.
- Post-assertion production Sync `34107210145`, attempt 1: success.
- Unchanged rerun of the same production Sync, attempt 2 / job `101696222176`: success; `817 passed in 5.67s`; final generated-context step reported `Context is already current.` and made no generated-context commit.

## Acceptance

All production acceptance gates are satisfied. This finding is production-complete and may increment maintenance `completed_count` exactly once (188 → 189). Continue with the next live blocker selected by `scripts/canonical_findings.py::active_findings` semantics.

# Canonical finding completion — Kyoto Himba Stakes precedence

Finding: `cf-528fb1894e2fccc1` (`京都赛马娘锦标`)

## Resolution

- Canonical identity: `Kyoto Himba Stakes`
- Locked term: `race.kyoto_himba_stakes`
- The reusable component rule `race.uma_musume_stakes.component131` excludes the exact full source so the component cannot override the full race identity.
- Regression seed preserves the live `suggested_targets_vi = ["Kyoto Himba Stakes"]` semantics.
- A live-state regression now asserts the finding resolves through the locked term and is absent from `active_findings`.

## Durable evidence

- Source precedence rule previously persisted: `b8a3b433baefb9afd7c799a2de7e6d7f7a668807`.
- Regression invariant commit: `3a82b22c6803ef5593699f974ffe8c2d9fb9a915`.
- Live-state assertion commit: `64403383f2a3b25bc40cf7fbf59d734e4118401a`.
- Initial production Sync: run `34106838703`, attempt 1 — success; all hardeners, finding refresh/resolution, queue build, pytest, and persistence passed.
- Validate run `34107210247` on the live-state assertion commit — pytest, `tlvi validate`, and index steps passed.
- Unchanged production Sync: run `34106838703`, attempt 2 — success; all hardeners, finding refresh/resolution, queue build, pytest, and persistence passed.
- After attempt 2, live `main` remained at the existing maintenance checkpoint commit with no generated-context commit, proving the context pipeline was semantically no-op.

This finding is production-accepted and may increment the maintenance completion counter by exactly one.

# Canonical findings maintenance — post-Hello-Polaris triage

Claim: `canonical-findings-maintenance-gpt56sol-auto11-20260904T0201Z`

## Completed in this claim

`cf-7af7f3692f9a938f` / `Hello 北极星` is production-accepted as `Hello Polaris` via `song.hello_polaris`.

Acceptance evidence:

- Validate `33826454594`: success.
- Sync translation context `33826454608`: success.
- Sync translation review plan `33826454592`: success.
- live review generation `tr-p3-67f8551f7780-6b63119b0563-b5c0bcb3bd-2544610eef` embeds `song.hello_polaris` / `Hello Polaris` and no longer carries `cf-7af7f3692f9a938f`.
- maintenance `completed_count` advanced from 77 to 78 only after those acceptance conditions were verified.

Primary implementation/acceptance checkpoint:
`work/orchestration/checkpoints/canonical-findings-20260904-hello-polaris-implementation.md`.

## Next-target triage

Do not guess these evidence-blocked findings:

- `cf-735331afc1ace008` / `奔跑到何处`: maps to JP `どこまで走れば`, but English/canonical naming evidence remains weaker than required.
- `cf-b74bd0c4b24ab2af` and `cf-b7da98397b071d2c`: Drowa-related findings remain evidence-blocked.

A possible terminology finding observed in the current review generation is `cf-15165b78a43e8c28` around the `青春燃烧` / Aoharu-combustion family. Before touching it, inspect existing Aoharu hardening rather than creating a duplicate fix:

- `scripts/harden_aoharu_ignition_finding.py` explicitly distinguishes `点燃青春` = `アオハル点火` from `燃烧青春` = `アオハル燃焼`.
- `work/orchestration/checkpoints/canonical-findings-20260903-aoharu-regenerated-complete.md` records the already-completed regenerated Aoharu Ignition finding `cf-7894d0578d8c8a02` with target `Thắp lửa thanh xuân`.
- therefore the next maintainer should first prove whether `cf-15165b78a43e8c28` is a distinct combustion-family canonical gap, a stale/generated finding, or a resolver-parity issue. Do not reuse the Ignition target for the combustion family and do not patch localized examples directly.

If that finding is genuinely distinct and the live locked terminology already provides an authoritative combustion-family target, implement a systemic hardener/regression and require Validate + Sync translation context + Sync translation review plan + live regenerated finding disappearance before incrementing `completed_count`.

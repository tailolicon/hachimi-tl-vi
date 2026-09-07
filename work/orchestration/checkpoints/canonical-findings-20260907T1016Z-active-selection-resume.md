# Canonical findings maintenance checkpoint — active selection resume

Claim: `canonical-findings-maintenance-gpt56sol-auto11-20260907T1011Z`
Worker: `gpt56sol-auto11-20260907-1711-maintenance`

## Live routing verification

- `WORKER_START.md` and live orchestration state were re-read from `main` before claiming.
- The maintenance lane was `released`, so this worker claimed it before deeper ledger inspection, preserving `completed_count: 190` and the prior completed evidence for `cf-70b5883f9b7068e2`.
- `scripts/canonical_findings.py::active_findings` semantics on live `main`: only `open`/`deferred` findings without `canonical_resolution` and without an explicit `ignore` review resolution are active blockers.

## Ledger inspection completed

- Fresh `glossary/canonical_findings.json` blob SHA: `5ecc2d765227a1895f1d931349508e9fc0a74fb2`.
- Direct blob inspection confirms null canonical resolutions must not be treated as blockers blindly: at least the Yoshiko and Hikari NPC rows have `canonical_resolution: null` but explicit `review_resolution.action: ignore`, so they are excluded by `active_findings`.
- A repository-wide search also surfaced older checkpoints; these are historical evidence only and must not be used to select the next live blocker without re-validating the current ledger.

## Resume instruction

Continue from the fresh blob above and identify the first current row satisfying the exact `active_findings` predicate. Do not revisit `cf-70b5883f9b7068e2` unless fresh evidence invalidates its completed resolution. Do not select ignored NPC findings merely because their canonical resolution is null. Once a live blocker is selected, perform the narrow canonical hardening required by its source scope and run the production validation/sync acceptance required by `WORKER_START.md`/`AUTOPILOT.md`.

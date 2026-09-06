# Canonical finding — Rhein Kraft Power context resolved

Resolved active context finding `cf-09030893aa309ee4` for zh-CN `私服（莱茵力量）`.

- The finding reports that the generic stat alias `力量` must not match inside the character name `莱茵力量` (Rhein Kraft).
- The live `common.stat.power` hardener already excludes `莱茵力量`, but the context resolver did not register this exact-source finding ID, leaving the canonical finding active despite the overmatch already being neutralized.
- Added `cf-09030893aa309ee4` to the proven Power context-guard set. Resolution remains evidence-gated: the resolver only closes it while the live Power matcher does not match the finding evidence.
- Added regression coverage for exact source `私服（莱茵力量）` / current `Thường phục (Line Kraft)`.
- `resolve_context_guard_findings.py` now sets `canonical_resolution` to `{layer: context_guard, term_id: common.stat.power, target_vi: Power}` for this finding.
- Active-finding semantics decreased from 148 to 147.
- Regression validation: `tests/test_item_power_context_guard_resolution.py` + `tests/test_context_guard_finding_resolution.py` -> `4 passed`.

Integrated to live `main` at commit `6c56a87b946bbe70622a2f96d83a996ec37893d0` via a non-forced fast-forward after rebasing over concurrent review/README commits.

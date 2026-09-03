# Canonical finding checkpoint — Aptitude `资质`

Finding: `cf-f333ff6a5cd11893`

## Evidence

Live `active_findings` originally reported this terminology finding for `资质`, with suggested target `Aptitude`, high confidence, and evidence at `localize_dict.json` key `SingleMode701028` (entering a race with low aptitude).

A scan of the then-current retrospective plan found 12 `localize_dict.json` items using `资质`, all in the player-facing Aptitude system: track aptitude (`场地资质`), distance aptitude (`距离资质`), running-style aptitude (`脚质资质`), Aptitude Sparks/requirements, and low-Aptitude race warnings. No reviewed localize occurrence used `资质` as a generic non-gameplay talent/qualification concept.

The repository already had canonical `common.aptitude` → `Aptitude` for `適性` / `适性`, plus `scripts/harden_aptitude_alias_finding.py` for the zh-CN UI variant `适应性`. Reuse that same scoped variant rule rather than creating a competing canonical term.

## Durable changes

- `scripts/harden_aptitude_alias_finding.py` updated on `main` at commit `aaa66b4b0badd0fc82f910c954679cc8df81f15e` so `common.aptitude.zhcn_variant` accepts both `适应性` and `资质`, remains scoped to `localize_dict.json`, and resolves to `Aptitude`.
- `tests/test_aptitude_alias_finding_hardening.py` updated on `main` at commit `6db369003d55bdf0a13075161be424bd54620101` with a regression case using the exact `SingleMode701028` low-Aptitude warning.
- The local execution backend did not have pytest installed at authoring time. Direct hardener/idempotence/matcher assertions passed, including `资质` matching `Aptitude` in `localize_dict.json` while an unrelated story-path use remained unmatched.

## Production acceptance

- Sync translation context run `33771131066` for head `6db369003d55bdf0a13075161be424bd54620101` completed successfully.
- Sync translation review plan run `33771130925` for the same head completed successfully.
- The review-plan production job ran `scripts/harden_aptitude_alias_finding.py` and reported `aptitude_alias_hardening_changed=false`, proving the live checkout already contained the durable hardener before canonical refresh.
- Production canonical refresh/guard processing completed, and the full production test suite passed: `553 passed in 5.17s`.
- The review-plan generation observed the new canonical context and produced a refreshed active review identity (`tr-p3-67f8551f7780-e722ef6a9fdc-b5c0bcb3bd-705d5babaa`, candidate count 4212 at generation time), so workers must follow live routing rather than continue assuming the prior plan is current.
- A fresh checkout of live `main` after both Sync runs directly loaded `glossary/canonical_findings.json`. `cf-f333ff6a5cd11893` now has `canonical_resolution={layer: community, term_id: common.aptitude.zhcn_variant, target_vi: Aptitude}`.
- Running `scripts.canonical_findings.active_findings` against the same live checkout returned 212 active findings and `still_active=False` for `cf-f333ff6a5cd11893`.

## Completion

Production acceptance is complete. `cf-f333ff6a5cd11893` is canonically resolved to `Aptitude` through the scoped `common.aptitude.zhcn_variant` rule and no longer blocks retrospective translation review. Maintenance completion count may advance from 29 to 30.

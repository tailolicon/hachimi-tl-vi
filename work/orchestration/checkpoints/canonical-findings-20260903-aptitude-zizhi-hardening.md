# Canonical finding checkpoint — Aptitude `资质`

Finding: `cf-f333ff6a5cd11893`

## Evidence

Live `active_findings` reports this terminology finding for `资质`, with suggested target `Aptitude`, high confidence, and evidence at `localize_dict.json` key `SingleMode701028` (entering a race with low aptitude).

A scan of the current retrospective plan found 12 `localize_dict.json` items using `资质`, all in the player-facing Aptitude system: track aptitude (`场地资质`), distance aptitude (`距离资质`), running-style aptitude (`脚质资质`), Aptitude Sparks/requirements, and low-Aptitude race warnings. No current-plan localize occurrence was found using `资质` as a generic non-gameplay talent/qualification concept.

The repository already has canonical `common.aptitude` → `Aptitude` for `適性` / `适性`, plus `scripts/harden_aptitude_alias_finding.py` for the zh-CN UI variant `适应性`. Reuse that same scoped variant rule rather than creating a competing canonical term.

## Durable changes

- `scripts/harden_aptitude_alias_finding.py` updated on `main` at commit `aaa66b4b0badd0fc82f910c954679cc8df81f15e` so `common.aptitude.zhcn_variant` accepts both `适应性` and `资质`, remains scoped to `localize_dict.json`, and still resolves to `Aptitude`.
- `tests/test_aptitude_alias_finding_hardening.py` updated on `main` at commit `6db369003d55bdf0a13075161be424bd54620101` with a regression case using the exact `SingleMode701028` low-Aptitude warning.
- The local execution backend does not have pytest installed. Direct hardener/idempotence/matcher assertions passed, including `资质` matching `Aptitude` in `localize_dict.json` while an unrelated story-path use remains unmatched.

## Acceptance continuation

Do not increment maintenance completion count for `cf-f333ff6a5cd11893` yet. Wait for the push-triggered production Sync workflows, verify tests and canonical refresh succeed, then directly confirm the live `glossary/canonical_findings.json` record has a canonical resolution targeting `Aptitude` and that `scripts.canonical_findings.active_findings` excludes this finding. Only then advance the maintenance count from 29 to 30.

# Canonical finding checkpoint — historical 1600万下 pending sync

Finding: `cf-493004166ae49fae`
Source: `1600万下`
Scope: `localize_dict.json`, exact match
Target: `Hạng dưới 16 triệu yên`
Claim: `canonical-findings-maintenance-gpt56sol-auto11-20260907T0256Z`

## Evidence and decision

- The live finding identifies `1600万下` as a historical race-class system label and reports the current Vietnamese `Dưới 16 triệu`, which drops both the class context and the omitted currency unit.
- JRA's own 2019 race material states that the current 1-win / 2-win / 3-win classes were formerly the 500万円以下 / 1000万円以下 / 1600万円以下 classes. JRA also explicitly labels `1600万下` as the current `3勝クラス` in historical race analysis.
- Preserve the historical label instead of silently modernizing it to `3-win class`, matching the already-established repository treatment for historical `1000万下`.
- Canonical Vietnamese target: `Hạng dưới 16 triệu yên`.

## Durable implementation

- Added `scripts/harden_historical_1600man_race_class_finding.py` on main at commit `8905663d5752d060ea372ad8ae36d7e5d1ebb7ac`.
- Added permanent idempotence / matching / canonical-resolution regression `tests/test_historical_1600man_race_class_finding_hardening.py` on main at commit `3dee078f5a0770433a0564e0d9cb1794fbdaaaf1`.
- The hardener adds a source-path-scoped exact community term and a lock review decision, and forbids legacy `Dưới 16 triệu`.

## Production validation status

- Push-triggered `Validate` run for head `3dee078f5a0770433a0564e0d9cb1794fbdaaaf1`: run `34078135058`, in progress at checkpoint.
- Push-triggered `Sync translation context` run for the same head: run `34078135042`, pending at checkpoint.

Do not advance `completed_count` until required validation and production context Sync succeed and the regenerated live finding has non-null canonical resolution. Continue this same finding from these run IDs.
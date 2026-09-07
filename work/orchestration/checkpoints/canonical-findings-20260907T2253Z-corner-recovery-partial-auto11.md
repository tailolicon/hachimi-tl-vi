# Canonical finding checkpoint — Corner Recovery

Finding: `cf-619bf2cec9f217a5` (`弯道回复○` / JP `コーナー回復○`).

## Durable repair

- Added permanent pre-apply hardener `scripts/harden_corner_recovery_finding.py` at `e54a3909bd9ae6f08d186ba874a4498247af8246`.
- Canonical target is `Hồi Phục Khúc Cua○`, matching `glossary/skill_name_style.json`; the hardener repairs reviewed term `reviewed.skill_name.ab9ceceded12` and its lock decision, superseding legacy `Khúc cua hồi phục○`.
- Added idempotence/regression coverage `tests/test_corner_recovery_finding_hardening.py` at `a6cdd4c096b00eecc7aa946c98b6e05b9cc5a98a`.

## Acceptance pending

At checkpoint time Validate run `34168098009` for the regression commit was still in progress. Production Sync translation context run `34168098017` was queued/pending behind the earlier run `34168092475`, which was still in progress. Do not count the finding complete yet.

Continuation: wait for a production Context Sync on a main head containing both commits to succeed; verify `cf-619bf2cec9f217a5` is inactive/resolved and the regenerated reviewed lock is `Hồi Phục Khúc Cua○`; then require a second successful unchanged/no-op production Context Sync. Only after that increment maintenance `completed_count` from 201 to 202. If any run fails, inspect the failing step and repair before acceptance.

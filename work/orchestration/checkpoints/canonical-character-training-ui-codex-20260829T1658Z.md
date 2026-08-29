# canonical-character-training-ui ready checkpoint — 2026-08-29T16:58Z

## Ownership and durable branch state

- Claim: `canonical-character-training-ui-codex-20260829T1651Z`.
- Deterministic branch: `canonical-character-training-ui-hardening`.
- Validated branch head before this checkpoint: `5d910ba3fa9bb5ed0ae46c67e22049fad095d83b`.
- Replayed against live `main` in GitHub Actions run `33264330026`; the workflow removed its temporary validation file after success.

## Permanent domain work

- Permanent hardener: `scripts/harden_character_training_ui_canon.py`.
- Materialized scoped canonical records for Career, Trainee, Goal Race, Turn, Rating, Team Rating, Scenario, and Room Match Track.
- Added Trainee-form exclusions so generic Umamusume world terminology does not overmatch `育成赛马娘` / `育成\n赛马娘`.
- Added focused positive/negative regressions for Career UI, aptitude grades, scoped source identity, source sync, and prose-negative behavior.
- No `localized_data/**` examples were patched.

## Acceptance evidence

GitHub Actions run `33264330026` passed:

- hardener run and second unchanged-run diff hash equality (idempotence);
- full pytest: **232 passed**;
- `tlvi validate`: **ok=true**, zero errors and zero warnings;
- `tlvi index`: **ok=true**, 8 files indexed.

The temporary replay/validation workflow was deleted by the successful run and is absent from the branch.

## Integration handoff

This domain is ready for serial integration. The primary lane must compare/reconstruct against then-live `main`, preserve other domains, run production Sync plus the second unchanged no-op Sync, and perform representative positive/negative spot checks before marking the domain complete.

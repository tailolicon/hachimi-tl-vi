# Canonical finding: 永井正道 / Masamichi Nagai

- Live finding: `cf-1bd479584e40d767`
- Source alias: `永井正道`
- Canonical Latin spelling: `Masamichi Nagai`
- Source scope: `text_data_dict.json`, `match_mode: contains`

## Evidence and rationale

The finding was originally created to stop Skill alias `正道` from overmatching inside creator name `永井正道`. That exclusion is already durable in `skill.righteous_path`. The remaining player-facing creator credit still needs its own proper-name canonical identity.

POPHOLIC's official creator profile lists `永井 正道` as `Masamichi Nagai` and explicitly names Umamusume: Pretty Derby `はじまりのSignal` among his works. MusicBrainz independently credits `永井正道 (Masamichi Nagai)` on Umamusume WINNING LIVE 01. This supports a full-name proper-name rule without weakening the existing Skill-substring exclusion.

## Durable implementation

- Hardener: `scripts/harden_masamichi_nagai_finding.py` (`12c5fabda5ec362058c1f395d27c1d2b2763e98e`)
- Regression tests: `tests/test_masamichi_nagai_finding_hardening.py` (`629fa76e1b026a69e49d397f33cd4cdcd60f7a02`)
- Canonical target: `Masamichi Nagai`
- The test verifies canonical resolution of the full-name finding while preserving `永井正道` in `skill.righteous_path.exclude_source_contains`; another-source-file coverage remains negative.

## Production acceptance state

Push-triggered workflows from the regression-test commit include Sync translation context run `33766266321`; Validate and review-plan sync were also triggered by the same push.

Do not increment maintenance `completed_count` or call `cf-1bd479584e40d767` complete until validation succeeds and production Sync materializes the proper-name canonical resolution on live `main`.

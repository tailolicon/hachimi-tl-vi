# Canonical finding implementation — ドロワダンスパート

Finding: `cf-b74bd0c4b24ab2af`

The prior research checkpoint established that the complete title has no sufficiently authoritative official/catalog Latin rendering. Keeping this one-off title as a project-wide canonical blocker would force workers either to guess a Romanization or defer forever.

## Durable implementation

- Added `scripts/harden_drowa_dance_part_finding.py` at commit `40c82d9eddc521c6c0302187d24d6a6364ff7ea6`.
- Added `tests/test_drowa_dance_part_finding_hardening.py` at commit `5e3fb1f4ead6fb10b6d1f86c39956aa6b4328c80`.
- The hardener records an explicit `ignore` terminology-review decision for the one-off exact title, scoped to `text_data_dict.json` item `16/1080`; it intentionally does **not** create `Drowa Dance Part` or another inferred Latin canonical term.
- Regression proves hardener idempotence, refresh of `review_resolution.action == ignore`, no synthetic canonical resolution, and removal from `active_findings(...)`.

## Acceptance gate

Push-triggered production workflows for head `5e3fb1f4ead6fb10b6d1f86c39956aa6b4328c80` were registered:

- Sync translation review plan: `33829770995` — pending at observation time.
- Sync translation context: `33829770978` — pending at observation time.
- Validate is also expected from the push-trigger set; do not increment maintenance completion until required validation/sync workflows succeed and the regenerated live finding carries explicit ignore / no longer blocks the live review item.

Maintenance `completed_count` remains unchanged pending production acceptance.

# Canonical finding checkpoint — Room Match replay pending validation/sync

Finding: `cf-52ac352454cf3a80`
Source: `房间竞赛`
Scope: `localize_dict.json`, key `RoomMatch400029`, contains match
Canonical target: `Room Match`
Claim: `canonical-findings-maintenance-gpt56sol-auto11-20260907T0256Z`

## Live finding

The finding reports the Room Match same-conditions replay prompt using `Đua Phòng`, while the repository already has established player-facing `Room Match` terminology scoped only to `RoomMatch0001`.

## Durable implementation

- Extended `scripts/harden_room_match_finding.py` to cover both audited keys `RoomMatch0001` and `RoomMatch400029`, preserving item-scoped matching and adding both observed Vietnamese calque capitalizations to the forbidden forms. Commit: `eeff2c5eddcf534fafac186c147566df2f347db3`.
- Extended `tests/test_room_match_finding_hardening.py` with a replay-prompt regression that verifies `RoomMatch400029` matches `mode.room_match` while unrelated keys remain excluded. Commit: `2413a1b6b7c0fdec47d79a8ce113e56aaa03349f`.

## Validation status

Push-triggered runs for test head `2413a1b6b7c0fdec47d79a8ce113e56aaa03349f`:
- Validate: `34078469040` (queued at checkpoint).
- Sync translation context: `34078469060` (pending at checkpoint).

Do not advance `completed_count` beyond 172 until production validation succeeds and the regenerated live finding resolves `cf-52ac352454cf3a80` to `Room Match`.
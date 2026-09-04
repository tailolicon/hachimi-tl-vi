# Canonical finding checkpoint — Champions Meeting newline alias

Finding: `cf-1de7f10f817c5866`
Source: `群英\n月赛`
Scope: `localize_dict.json`, exact match
Target: `Champions Meeting`

## Live diagnosis

The current generated finding is an exact newline-form `localize_dict.json` label at `RoomMatch600018`, currently translated as `Giải đấu\ntháng`. The repository already has an accepted lock for the flattened source label `群英月赛` as official Global `Champions Meeting` (`parallel.ctx-67f8551f77807292-v1.term-0129.11`), and generated translation regressions explicitly reject `Monthly Match` for this event identity.

## Durable implementation

- Hardener commit: `2be0379fb0028d8ce85fef1dade40defcbf9b99c`
- Hardener: `scripts/harden_champions_meeting_newline_finding.py`
- Regression-test commit: `0eb771061685e82016c6e5ec37dc125fd5473850`
- Tests: `tests/test_champions_meeting_newline_finding_hardening.py`
- Rule is item-scoped, `source_paths = [localize_dict.json]`, `match_mode = exact`, and does not broaden the newline alias to unrelated source forms/files.

## Validation / production gates

- Validate run `33918296859`: **success**.
- Sync translation context run `33918296831`: pending at the latest check.
- Sync translation review plan run `33918296860`: pending at the latest check.

Do **not** increment maintenance `completed_count` yet. Production acceptance requires successful context sync, read-back of the generated finding resolving to `Champions Meeting`, and a review-plan sync that runs against the post-context state.

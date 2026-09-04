# Canonical finding checkpoint — Champions Meeting newline alias

Finding: `cf-1de7f10f817c5866`
Source: `群英\n月赛`
Scope: `localize_dict.json`, exact match
Target: `Champions Meeting`

## Live diagnosis

The generated finding was an exact newline-form `localize_dict.json` label at `RoomMatch600018`, translated as `Giải đấu\ntháng`. The repository already has an accepted lock for the flattened source label `群英月赛` as official Global `Champions Meeting` (`parallel.ctx-67f8551f77807292-v1.term-0129.11`), and generated translation regressions explicitly reject `Monthly Match` for this event identity.

## Durable implementation

- Hardener commit: `2be0379fb0028d8ce85fef1dade40defcbf9b99c`
- Hardener: `scripts/harden_champions_meeting_newline_finding.py`
- Regression-test commit: `0eb771061685e82016c6e5ec37dc125fd5473850`
- Rule is item-scoped, `source_paths = [localize_dict.json]`, `match_mode = exact`, and does not broaden the newline alias to unrelated source forms/files.

## Production acceptance

- Validate run `33918296859`: **success**.
- Sync translation context run `33918296831`: **success**.
- Generated context read-back commit: `469f2e35ba2eebeeb2c47d419300cf47aec8bff2`; the finding resolves to locked `Champions Meeting`.
- Successor Sync translation review plan run `33918296860`: **success** (job `101172472438`).
- Live review plan regenerated to `tr-p3-67f8551f7780-d4f284aeb0df-b5c0bcb3bd-f537f0ed15`.
- Direct default-branch search for the active plan id together with `cf-1de7f10f817c5866` returns no match, confirming the regenerated live plan no longer carries this finding as a blocker. Historical review artifacts still contain the old open finding, as expected.

## Result

**Accepted complete.** This finding satisfies the production acceptance gates and may advance maintenance `completed_count` from 123 to 124.

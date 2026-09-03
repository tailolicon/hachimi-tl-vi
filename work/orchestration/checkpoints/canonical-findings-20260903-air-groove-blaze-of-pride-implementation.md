# Canonical finding implementation: Air Groove / Blaze of Pride

Finding: `cf-3b6a33d1c2346de5`

- zh-CN alias: `荣耀之刃`
- Repository Skill IDs from prior live research: `10180101` / `10180102` / `10180103`
- Character identity: game ID `1018` = Air Groove / `エアグルーヴ`
- Verified JP upgraded unique Skill identity: `ブレイズ・オブ・プライド`
- Canonical target: `Blaze of Pride`
- Historical target: `Lưỡi đao vinh quang`

## Scope and decision

The finding is an exact proper-name Skill finding in `text_data_dict.json`. Preserve the JP identity-bearing English/katakana title instead of calquing the zh-CN semantic bridge. The community rule is exact and file-scoped; it must not match longer prose or `localize_dict.json`.

## Implementation

- Hardener: `scripts/harden_air_groove_blaze_of_pride_finding.py`, commit `28e7e4af78b8c5e11a30298adb6613754d008c63`.
- Regression: `tests/test_air_groove_blaze_of_pride_finding_hardening.py`, commit `b46d7d78c7d2d803ecc5259af9f530d2a6e1f062`.
- Community rule: `skill.air_groove.blaze_of_pride`.
- Terminology decision: `audit.finding.skill-air-groove-blaze-of-pride`.
- Regression covers production-shape resolution, idempotence, exact-match negative case for longer text, and other-file exclusion.

## Acceptance pending

Do not increment maintenance completion count beyond 60 until Validate, production Sync translation context, and Sync translation review plan succeed on a descendant containing `b46d7d78c7d2d803ecc5259af9f530d2a6e1f062`, and a refreshed live plan embeds `skill.air_groove.blaze_of_pride` with `cf-3b6a33d1c2346de5` absent.

Observed runs created for regression head include Sync translation context `33816316294` and Sync translation review plan `33816316379`; both were pending at first observation.

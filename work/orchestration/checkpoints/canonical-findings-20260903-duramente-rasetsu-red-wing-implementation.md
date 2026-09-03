# Canonical finding implementation: 羅刹、赤翼にて天上へ至らん

Finding: `cf-15c84817094087db`

- zh-CN alias: `赤翼罗刹越九天`
- Repository Skill entries: category `147`, Duramente IDs `11080101` / `11080102` / `11080103`
- Character identity: game ID `1108` = Duramente / `ドゥラメンテ`
- Verified JP unique Skill: `羅刹、赤翼にて天上へ至らん`
- Canonical Vietnamese target: `Xích Dực La Sát Vượt Cửu Thiên`
- Historical target: `Xích Dực La Sát vượt cửu thiên`

## Evidence and naming decision

Repository character registry verifies game ID 1108 as Duramente. Current JP gameplay references from GameWith and Game8 independently identify her unique Skill as `羅刹、赤翼にて天上へ至らん`. The zh-CN bridge compresses the archaic image to `赤翼罗刹越九天`; the existing Vietnamese already preserves that image, so the canonical correction is a title-style normalization rather than a semantic rewrite.

## Scope

The live finding uses `match_mode: contains` in `text_data_dict.json` without a JSON-path prefix. The same full title may appear inside inheritance descriptions, so the rule remains file-scoped and prefix-free; it must not resolve matching text in `localize_dict.json`.

## Implementation

- Hardener: `scripts/harden_duramente_rasetsu_red_wing_finding.py`, commit `5a515a74a5064c472c1d12f99aa743739dcedd7e`.
- Regression: `tests/test_duramente_rasetsu_red_wing_finding_hardening.py`, commit `db6acaaf63a4e3ab77c5c6530dd01b134f8ddf39`.
- Community rule: `skill.duramente.rasetsu_red_wing`.
- Terminology decision: `audit.finding.skill-duramente-rasetsu-red-wing`.
- Regression covers resolution/idempotence, inheritance-text contains matching, and an other-file negative case.

## Acceptance pending

Do not increment maintenance completion count until Validate and production Sync translation context succeed and a refreshed active review plan embeds `skill.duramente.rasetsu_red_wing` with `cf-15c84817094087db` absent.

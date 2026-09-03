# Canonical finding implementation: ずっとずっと輝いて

Finding: `cf-7a3f2b970cbc7726`

- zh-CN alias: `永远闪耀下去`
- Repository Skill entries: category `147`, Rhein Kraft variant IDs `11090201` / `11090202` / `11090203`
- Character identity: game ID `1109` = Rhein Kraft / `ラインクラフト`
- Verified JP unique Skill: `ずっとずっと輝いて`
- Canonical Vietnamese target: `Mãi Mãi Tỏa Sáng`
- Historical target: `Mãi mãi tỏa sáng`

## Evidence and naming decision

Repository character registry verifies game ID 1109 as Rhein Kraft. Current JP gameplay references identify variant 110902's unique Skill as `ずっとずっと輝いて`. The zh-CN bridge `永远闪耀下去` and existing Vietnamese draft already preserve the meaning, so the canonical correction is title-style normalization rather than a semantic rewrite.

## Scope

The live finding uses `match_mode: contains` in `text_data_dict.json` without a JSON-path prefix. The full title may also occur in inheritance descriptions, so the rule remains file-scoped and prefix-free; it must not resolve matching text in `localize_dict.json`.

## Implementation

- Hardener: `scripts/harden_rhein_kraft_zutto_zutto_kagayaite_finding.py`, commit `8319aa90128a7b03a1bc727edb765bf67e9af462`.
- Regression: `tests/test_rhein_kraft_zutto_zutto_kagayaite_finding_hardening.py`, commit `abe90c2cc19cdd0bcaeb1bb251c43b2d88ed111b`.
- Community rule: `skill.rhein_kraft.zutto_zutto_kagayaite`.
- Terminology decision: `audit.finding.skill-rhein-kraft-zutto-zutto-kagayaite`.
- Regression covers production-shape resolution, idempotence, inheritance-text contains matching, and an other-file negative case.

## Acceptance pending

Do not increment maintenance completion count until Validate and production Sync translation context succeed and a refreshed active review plan embeds `skill.rhein_kraft.zutto_zutto_kagayaite` with `cf-7a3f2b970cbc7726` absent.

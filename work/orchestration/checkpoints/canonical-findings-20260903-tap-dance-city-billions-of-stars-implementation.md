# Canonical finding implementation: Billions of stars

Finding: `cf-c3e43ed4071450fb`

- zh-CN alias: `满天星斗`
- Repository Skill entries: category `147`, Tap Dance City IDs `11070101` / `11070102` / `11070103`
- Character identity: game ID `1107` = Tap Dance City / `タップダンスシチー`
- Verified JP unique Skill: `Billions of stars`
- Canonical target: `Billions of stars`
- Historical target: `Trời đầy sao`

## Evidence and naming decision

Repository character registry verifies game ID 1107 as Tap Dance City. Current JP gameplay references from GameWith and Game8 independently identify her unique Skill literally in English as `Billions of stars`. Therefore the canonical target preserves the source-game title verbatim rather than semantic-calquing the zh-CN bridge `满天星斗`.

## Scope

The live finding uses `match_mode: contains` in `text_data_dict.json` without a JSON-path prefix. The title can occur inside inheritance descriptions, so the rule remains file-scoped, prefix-free, and contains-matched. It must not affect `localize_dict.json` or generic star-related prose.

## Implementation

- Hardener: `scripts/harden_tap_dance_city_billions_of_stars_finding.py`, commit `f5fa2c1e9f1765dc16378cd5193db2006832c6f0`.
- Regression: `tests/test_tap_dance_city_billions_of_stars_finding_hardening.py`, commit `8467bfc0d6ca5d80d94b7b8b71d50853241d1b30`.
- Community rule: `skill.tap_dance_city.billions_of_stars`.
- Terminology decision: `audit.finding.skill-tap-dance-city-billions-of-stars`.
- Regression covers resolution/idempotence, inheritance-text contains matching, and an other-file negative case.

## Acceptance pending

Do not increment maintenance completion count until Validate and production Sync translation context succeed and a refreshed active review plan embeds `skill.tap_dance_city.billions_of_stars` with `cf-c3e43ed4071450fb` absent.

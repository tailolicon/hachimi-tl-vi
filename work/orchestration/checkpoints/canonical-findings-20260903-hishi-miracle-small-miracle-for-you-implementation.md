# Canonical finding implementation: 小さな奇跡、フォーユー♪

Finding: `cf-b6bef7c906165bcd`

- zh-CN alias: `赠予你的小小奇迹♪`
- Repository Skill entries: category `147`, Hishi Miracle variant IDs `11060201` / `11060202` / `11060203`
- Character identity: game ID `1106` = Hishi Miracle / `ヒシミラクル`
- Verified JP unique Skill: `小さな奇跡、フォーユー♪`
- Canonical Vietnamese target: `Kỳ Tích Nhỏ Dành Cho Bạn♪`
- Historical target: `Tặng bạn một kỳ tích bé nhỏ♪`

## Evidence and naming decision

Current JP gameplay references from GameWith and Game8 identify Hishi Miracle variant 110602's unique Skill as `小さな奇跡、フォーユー♪`. The canonical target keeps the complete “small miracle / for you” meaning and musical-note marker, but compresses it into a commercial-game title instead of a prose sentence. Title capitalization follows `glossary/skill_name_style.json`.

## Scope

The live finding uses `match_mode: contains` in `text_data_dict.json` without a JSON-path prefix. The title also occurs inside category-172 inheritance descriptions, so the rule intentionally remains file-scoped and prefix-free. It must not resolve a matching source in `localize_dict.json`.

## Implementation

- Hardener: `scripts/harden_hishi_miracle_small_miracle_for_you_finding.py`, commit `e5a40b058f72394c00188b851e7e1c67909d9069`.
- Regression: `tests/test_hishi_miracle_small_miracle_for_you_finding_hardening.py`, commit `6fef935a08c705bd2418d2fc93d0beaf77aab4ac`.
- Community rule: `skill.hishi_miracle.small_miracle_for_you`.
- Terminology decision: `audit.finding.skill-hishi-miracle-small-miracle-for-you`.
- Regression covers production-shape resolution, idempotence, inheritance-text coverage, and an other-file negative case.

## Acceptance pending

Do not increment maintenance completion count until Validate and production Sync translation context succeed and a refreshed active review plan embeds `skill.hishi_miracle.small_miracle_for_you` with `cf-b6bef7c906165bcd` absent.

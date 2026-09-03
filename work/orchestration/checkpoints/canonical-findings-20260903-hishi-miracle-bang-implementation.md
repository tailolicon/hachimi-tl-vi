# Canonical finding implementation: Bang☆ミラクるわせ！

Finding: `cf-5e182ae6c433e59d`

- zh-CN alias: `砰☆奇迹天降！`
- Repository Skill entries: category `147`, Hishi Miracle variant IDs `11060101` / `11060102` / `11060103`
- Character identity: game ID `1106` = Hishi Miracle / `ヒシミラクル`
- Verified JP unique Skill: `Bang☆ミラクるわせ！`
- Canonical Vietnamese target: `Bang☆Kỳ Tích Giáng Trần!`
- Historical target: `Bùm☆Kỳ tích giáng trần!`

## Evidence and naming decision

Repository character registry verifies game ID 1106 as Hishi Miracle. Current JP gameplay references from GameWith and Game8 independently list Hishi Miracle's unique Skill exactly as `Bang☆ミラクるわせ！`.

The canonical target preserves the distinctive English `Bang`, `☆`, and Miracle motif from JP while using the compact zh-CN title `砰☆奇迹天降！` as the Vietnamese compression/style guide. `Kỳ Tích Giáng Trần` keeps the existing concise imagery while normalizing commercial-game title capitalization. The historical target is rejected because it translates the identity-bearing `Bang` to `Bùm` and uses sentence-style capitalization.

## Scope

The finding itself uses `match_mode: contains` in `text_data_dict.json` without a JSON-path prefix. The complete title also occurs inside category-172 inheritance descriptions, so the canonical rule intentionally uses file-scoped `contains` matching without a category prefix. It must not cover `localize_dict.json` or generalize component words.

## Implementation

- Hardener: `scripts/harden_hishi_miracle_bang_finding.py`, commit `86fde84a64a6bbbc3ea19bb222723dd8a3e26497`.
- Regression: `tests/test_hishi_miracle_bang_finding_hardening.py`, commit `e6f4aa20923bc0966435f961115394f111094c74`.
- Community rule: `skill.hishi_miracle.bang_miracle`.
- Terminology decision: `audit.finding.skill-hishi-miracle-bang-miracle`.
- Regression covers production-shape resolution, idempotence, inheritance-text contains matching, and a negative other-file case.

## Acceptance pending

Do not increment maintenance completion count until Validate and production Sync translation context succeed and a refreshed active review plan embeds `skill.hishi_miracle.bang_miracle` with `cf-5e182ae6c433e59d` absent.

# Canonical finding implementation: 暁の御旗『葛城栄主』！

Finding: `cf-abda2b1124d162ff`

- zh-CN alias: `拂晓御旗『葛城荣主』！`
- Repository locator: `47:101041`
- Verified JP title: `暁の御旗『葛城栄主』！`
- Character: Katsuragi Ace
- Canonical Vietnamese target: `Ngự Kỳ Bình Minh 『Katsuragi Ace』!`
- Historical target normalized: `Ngự kỳ bình minh 『Katsuragi Ace』!`

## Evidence

Repository curation already verifies locator `47:101041` as JP `暁の御旗『葛城栄主』！` and explicitly warns that quoted `葛城栄主` is stylized character/kanji wordplay associated with Katsuragi Ace, so the Chinese proper-name spelling must not be literally calqued.

Fresh JP gameplay references independently identify Katsuragi Ace's unique Skill as exactly `暁の御旗『葛城栄主』！`; GameWith, Game8, and Umamusume Lab all agree on the title and effect. This closes the identity uncertainty that caused the earlier curation defer.

The existing Vietnamese title already makes the important proper-name treatment correctly: preserve `Katsuragi Ace` in Roman letters rather than translate `葛城栄主`/`葛城荣主`. `暁の御旗` is faithfully represented by `Ngự kỳ bình minh`; normalize only game-title capitalization to `Ngự Kỳ Bình Minh`.

## Scope decision

Canonicalize the complete Skill-title alias only, scoped to `text_data_dict.json`. The live finding appears inside category-172 inheritance descriptions, so matching must cover the full title inside longer strings without creating a generic rule for `拂晓`, `御旗`, or the character name independently.

## Implementation

- Hardener: `scripts/harden_katsuragi_ace_dawn_banner_finding.py`, commit `d09be5d54661e5933cd6c92e67ae5d25acf1f258`.
- Regression: `tests/test_katsuragi_ace_dawn_banner_finding_hardening.py`, commit `c7ffe677c36a9d9242b4cd78101183bb1f220d87`.
- Community rule: `skill.katsuragi_ace.akatsuki_no_mihata`.
- Terminology decision: `audit.finding.skill-katsuragi-ace-akatsuki-no-mihata`.
- Regression requires the exact live finding shape to resolve, proves idempotence, proves longer category-172 inheritance text is covered, and proves the alias does not resolve `localize_dict.json`.

## Acceptance pending

For regression commit `c7ffe677c36a9d9242b4cd78101183bb1f220d87`:

- Sync translation context run `33812227623`: pending at last check.
- Sync translation review plan run `33812227675`: pending at last check.
- Validate is also triggered by the same push and must pass before acceptance.

Do not increment maintenance completion count for `cf-abda2b1124d162ff` until Validate and production context sync succeed and a refreshed live review batch embeds `skill.katsuragi_ace.akatsuki_no_mihata` with this finding absent.

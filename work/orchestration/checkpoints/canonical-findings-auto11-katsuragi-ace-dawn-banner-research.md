# Canonical finding implementation: 暁の御旗『葛城栄主』！

Finding: `cf-abda2b1124d162ff`

- zh-CN alias: `拂晓御旗『葛城荣主』！`
- Repository locator: `47:101041`
- Verified JP title: `暁の御旗『葛城栄主』！`
- Character: Katsuragi Ace
- Canonical Vietnamese target: `Ngự Kỳ Bình Minh 『Katsuragi Ace』!`
- Historical target normalized: `Ngự kỳ bình minh 『Katsuragi Ace』!`

## Evidence

Repository curation verifies locator `47:101041` as JP `暁の御旗『葛城栄主』！` and warns that quoted `葛城栄主` is stylized character/kanji wordplay associated with Katsuragi Ace. Independent JP gameplay references agree on the same unique-Skill title. Preserve `Katsuragi Ace` in Roman letters rather than calquing `葛城栄主`/`葛城荣主`; normalize the established Vietnamese title to game-title capitalization.

## Scope and implementation

Canonicalize only the complete Skill-title alias in `text_data_dict.json`, using `contains` because the title appears inside category-172 inheritance descriptions.

- Hardener: `scripts/harden_katsuragi_ace_dawn_banner_finding.py`, commit `d09be5d54661e5933cd6c92e67ae5d25acf1f258`.
- Regression: `tests/test_katsuragi_ace_dawn_banner_finding_hardening.py`, commit `c7ffe677c36a9d9242b4cd78101183bb1f220d87`.
- Community rule: `skill.katsuragi_ace.akatsuki_no_mihata`.
- Terminology decision: `audit.finding.skill-katsuragi-ace-akatsuki-no-mihata`.
- Regression proves production-shape resolution, idempotence, longer inheritance-text coverage, and no resolution in `localize_dict.json`.

## Production acceptance

Accepted on live `main`.

- Validate run `33812227657`: completed/success.
- Sync translation context run `33812227623`: completed/success; generated context commit `955a2d012d48ca94739ec2051cd29db141201ce4`.
- Sync translation review plan run `33812211892`: completed/success. The workflow checks out latest `origin/main`, so it incorporated the live context/hardener state.
- Refreshed active plan: `tr-p3-67f8551f7780-f5911550c8f3-b5c0bcb3bd-2a3db94f63`.
- Live batch `...-b0213` embeds `skill.katsuragi_ace.akatsuki_no_mihata`, preferred/accepted target `Ngự Kỳ Bình Minh 『Katsuragi Ace』!`, forbidden historical lower-case form, and `canonical_findings: []` for the `拂晓御旗『葛城荣主』！` entries.

Finding `cf-abda2b1124d162ff` is therefore accepted/resolved for maintenance accounting.

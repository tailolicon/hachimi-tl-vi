# Canonical finding implementation checkpoint: かがやけ☆とまこまい

- Finding: `cf-17348d85370763d1`
- zh-CN source: `闪耀☆苫小牧`
- JP identity: `かがやけ☆とまこまい`
- Character: Hokko Tarumae
- Proposed/locked Vietnamese target: `Tỏa sáng☆Tomakomai`

## Evidence

The live retrospective review plan marks `cf-17348d85370763d1` as an open proper-name finding for the Skill title `闪耀☆苫小牧`. Public JP references identify Hokko Tarumae's unique Skill as `かがやけ☆とまこまい`; the existing Vietnamese text already preserves the title's meaning and Tomakomai place name, so this maintenance change avoids unnecessary text churn and hardens only canonical infrastructure.

## Durable implementation

- `scripts/harden_kagayake_tomakomai_finding.py` — commit `c488a25aca5ea22c6f4811ef332fcf31bef8ec0d`
  - adds exact community canonical term `skill.kagayake_tomakomai`;
  - adds explicit review lock `audit.finding.skill-kagayake-tomakomai`;
  - scopes matching to exact `text_data_dict.json` Skill title;
  - adds the canonical target to the finding suggestions.
- `tests/test_kagayake_tomakomai_finding_hardening.py` — commit `2a7146f4dadc3d11d8b8802d76e14101a4768c62`
  - verifies idempotence;
  - verifies canonical/review resolution removes the synthetic live-shape finding from `active_findings`;
  - verifies the exact rule does not overmatch longer source text or another source file.

## Pending acceptance

GitHub Actions `Validate` run `33786355399` and `Sync translation review plan` run `33786355429` were queued/pending when this checkpoint was written. Do not increment maintenance `completed_count` for this finding until validation succeeds, production context sync/regeneration has run, and the regenerated active review plan no longer embeds `cf-17348d85370763d1` as a blocker.

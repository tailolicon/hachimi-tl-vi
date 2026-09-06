# Canonical finding hardening — Pure Prayer / Holy Light

Claim: `canonical-findings-maintenance-gpt56sol-auto11-20260906T203810Z`

Finding: `cf-6bac54ad4992b471`

## Live blocker

- zh-CN: `无垢之祷·圣洁之光`
- live current text in retrospective context: `Lời nguyện tinh khôi · Ánh sáng thánh khiết`
- finding source path: `text_data_dict.json`
- previous curation deferred only because the exact Japanese display title had not been verified.

## New identity evidence

Current JP game references now identify Red Desire's unique Skill as `無垢の祈り・ホーリーライト` and tie it to ★3 `[Divine Raiment] レッドディザイア`. This removes the identity uncertainty recorded by the August curation defer. The JP and zh-CN titles agree in imagery rather than conflict.

Repository `glossary/skill_name_style.json` requires a compact commercial-game ability title, source-symbol preservation, Japanese semantic guarding, and Vietnamese game-title capitalization. The selected canonical target is `Lời Nguyện Tinh Khôi・Thánh Quang`: it keeps the two-part title and JP interpunct, renders 無垢の祈り naturally, and compresses ホーリーライト / 圣洁之光 to the concise `Thánh Quang` rather than the older long prose-like second half.

Public JP verification consulted:

- Game8, `無垢の祈り・ホーリーライト` Skill page, updated 2026-09-01.
- GameBiz/Cygames announcement for Red Desire, confirming the unique Skill name and Red Desire identity.

## Hardening implemented

- `scripts/harden_pure_prayer_holy_light_finding.py`
  - exact source alias `无垢之祷·圣洁之光`
  - source-path coverage `text_data_dict.json`
  - supported `invalidation_scope: item`
  - target `Lời Nguyện Tinh Khôi・Thánh Quang`
  - JP alias `無垢の祈り・ホーリーライト`
  - historical long target forbidden
  - terminology review decision `audit.finding.skill-red-desire-pure-prayer-holy-light`.
- `tests/test_pure_prayer_holy_light_finding_hardening.py`
  - idempotence
  - canonical + review resolution
  - exact source/path non-overmatch
  - two-part interpunct preservation.

Implementation commits:

- hardener: `39adebfe38ca34ee9b051e175632a1e1230e6817`
- regression test: `9ea5bdd23924f438e25f56d3c90ee6e941da58a5`

## Completion gate

Do not increment maintenance `completed_count` yet. Require Validate plus successful production context Sync, then verify live `glossary/canonical_findings.json` records a non-null canonical resolution for `cf-6bac54ad4992b471` and that newly generated review context no longer carries this blocker.

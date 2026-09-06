# Canonical finding hardening — Pure Prayer / Holy Light

Claim: `canonical-findings-maintenance-gpt56sol-auto11-20260906T203810Z`

Finding: `cf-6bac54ad4992b471`

## Repository evidence and identity verification

The live blocker was zh-CN `无垢之祷·圣洁之光`, previously rendered `Lời nguyện tinh khôi · Ánh sáng thánh khiết`. Older repository curation deferred only because the exact Japanese display title had not been verified.

Current JP references identify Red Desire's unique Skill as `無垢の祈り・ホーリーライト`, removing that identity uncertainty. Repository `glossary/skill_name_style.json` calls for a compact commercial-game title with source-symbol preservation and Japanese semantic guarding. The selected canonical target is `Lời Nguyện Tinh Khôi・Thánh Quang`, preserving the two-part title/interpunct while keeping the Vietnamese title compact.

## Hardening implemented

- `scripts/harden_pure_prayer_holy_light_finding.py`
  - exact source alias `无垢之祷·圣洁之光`
  - source-path coverage `text_data_dict.json`
  - supported `invalidation_scope: item`
  - target `Lời Nguyện Tinh Khôi・Thánh Quang`
  - JP alias `無垢の祈り・ホーリーライト`
  - historical long target forbidden
  - review decision `audit.finding.skill-red-desire-pure-prayer-holy-light`.
- `tests/test_pure_prayer_holy_light_finding_hardening.py`
  - idempotence
  - canonical + review resolution
  - exact source/path non-overmatch
  - two-part interpunct preservation.

Implementation commits:

- hardener: `39adebfe38ca34ee9b051e175632a1e1230e6817`
- regression test: `9ea5bdd23924f438e25f56d3c90ee6e941da58a5`

## Validation / integration

- Validate run `34058762662` completed successfully for the regression-test commit.
- Production Sync translation context run `34058748621` completed all hardeners, terminology application, context pipeline tests, and generated-context commit successfully.
- Generated context commit: `86c61f12a6df80546c11dc702d7c1799dbc8ccf1`.
- Live `glossary/canonical_findings.json` now records for `cf-6bac54ad4992b471`:
  - `suggested_targets_vi: ["Lời Nguyện Tinh Khôi・Thánh Quang"]`
  - `canonical_resolution.layer: locked`
  - `canonical_resolution.target_vi: "Lời Nguyện Tinh Khôi・Thánh Quang"`
  - review decision `audit.finding.skill-red-desire-pure-prayer-holy-light`, action `lock`.
- The generated terminology queue reduced `open_canonical_findings` from 155 to 154.
- The reviewed registry now carries JP `無垢の祈り・ホーリーライト` and exact zh-CN `无垢之祷·圣洁之光` for the new locked term.

## Status

Complete. This maintenance unit may increment the shared maintenance completed count from 153 to 154. Re-route from live `WORKER_START.md`; other canonical findings and retrospective review work remain.

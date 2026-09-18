# Canonical finding implementation — North Flight / Shining Runway (2026-09-18)

Finding: `cf-7997ce8ec3a6a1ee`
zh-CN bridge title: `闪亮跑道`
Canonical target: `Shining Runway`

## Evidence

- Inheritance rows `10820101`–`10820103` bind this repeated Skill title to character family `1082`.
- The factor record for `10820101` identifies the Skill name as `Shining Runway`.
  - https://wiki.biligame.com/umamusume/%E5%9B%A0%E5%AD%90%3AShining_Runway
- JP card `[Looking Fly!] North Flight` lists its unique Skill as the exact English display string `Shining Runway`.
  - https://xn--gck1f423k.xn--1bvt37a.tools/cards/108201
  - https://umamusu.wiki/Game%3ANorth_Flight_%28Looking_Fly%21%29
- Because the original JP display title is already English, preserving `Shining Runway` does not require inventing a Global/English localization.

## Permanent fix

- Add `scripts/harden_shining_runway_finding.py`.
- Add reviewed lock `audit.finding.skill-north-flight-shining-runway`.
- Scope the rule to `text_data_dict.json`, exact source alias `闪亮跑道`, item invalidation only.
- Forbid the historical zh-CN-derived Vietnamese calque `Đường chạy lấp lánh`.
- Add `tests/test_shining_runway_finding_hardening.py` covering idempotence, canonical resolution, wrong source path, and prose-containing alias rejection.

## Pre-publication validation

- Shiro host-side resolver regression using an isolated temporary glossary: `3/3 passed`.
- No direct edit to `localized_data/**`.

Next: publish atomically, run Validate, production Sync, verify the live finding is inactive and locked to `Shining Runway`, then run a second unchanged Sync before incrementing maintenance `completed_count`.

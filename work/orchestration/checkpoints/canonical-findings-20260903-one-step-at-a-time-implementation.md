# Canonical finding implementation: 稳步前行 / 一歩ずつ前へ

Finding: `cf-df8f8811150b46f9`

- zh-CN source: `稳步前行`
- Verified JP Skill: `一歩ずつ前へ`
- Pinned locator: `47:203362`
- Canonical Vietnamese target: `Từng bước tiến lên`
- Historical target to replace: `Tiến bước vững vàng`

## Evidence and reasoning

Existing curation `work/curation/results/term-0070/sol-ctx-20260826T110047Z-422b638a.json` already verified locator `47:203362` as JP `一歩ずつ前へ` and reviewed `Từng bước tiến lên` as the Vietnamese lock. The live finding exists because durable reviewed term `reviewed.skill_name.321d0fec9832` for the distinct zh-CN title `前行` / JP `前列狙い` was still matching inside `稳步前行`.

## Implementation

- Context/canonical hardener: `scripts/harden_one_step_at_a_time_context_finding.py` at commit `21e978b10383b2fc80e2ddf9df993b5cdef43d46`.
- Regression tests: `tests/test_one_step_at_a_time_context_finding_hardening.py` at commit `2994c6604e03854e2291d8bde404b3b6671bb4a4`.
- The hardener narrows `reviewed.skill_name.321d0fec9832` to exact-only matching, so `前行` retains canonical `Nhắm Tuyến Đầu` while no longer overmatching `稳步前行`.
- It adds exact category-147 community rule `skill.one_step_at_a_time` and terminology decision `audit.finding.skill-one-step-at-a-time` for `稳步前行` → `Từng bước tiến lên`, backed by JP `一歩ずつ前へ`.
- It supplies the reviewed target to `cf-df8f8811150b46f9`, allowing canonical refresh to resolve the finding positively rather than merely suppressing it.

## Remaining acceptance

Require successful Validate, production Sync translation context, refreshed review plan, and live context proving `cf-df8f8811150b46f9` absent while `skill.one_step_at_a_time` is embedded and the `前行` lock no longer overmatches.

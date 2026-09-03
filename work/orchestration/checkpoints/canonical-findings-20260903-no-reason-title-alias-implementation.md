# Canonical finding implementation: No Reason title alias

- Finding: `cf-a73e3962c7a5f8a8`
- zh-CN category-147 source: `知宵欺敌,百战不殆`
- Existing factor alias: `知宵欺敌 百战不殆`
- Verified JP unique Skill title: `知宵欺敵、百戦不殆`
- Character identity: No Reason / ノーリーズン (game ID 1096)
- Existing canonical Vietnamese target reused: `Thấu thời lừa địch, trăm trận không nguy`
- Historical title target rejected: `Biết ta biết địch, trăm trận không nguy`

## Systemic resolution

The repository already had canonical rule `skill.no_reason.zhixiao_baizhan` and completed finding `cf-0fe33e249eca596b` for the space-form alias used inside inheritance-factor text. The new live finding is not a different Skill: it is the same JP identity exposed as a category-147 title with an ASCII comma.

Rather than introduce a competing title, the existing hardener now recognizes both zh-CN punctuation variants and appends the established canonical target to both ledger findings. A title-specific review lock mirrors the live exact/category-147 scope, while the shared community rule retains `contains` mode because the original space-form alias legitimately occurs inside longer factor descriptions.

## Implementation

- Extended hardener: `scripts/harden_no_reason_zhixiao_finding.py` at commit `18cd06107e6ff31a6737f8016b5913b49982eae5`.
- Extended regression tests: `tests/test_no_reason_zhixiao_finding_hardening.py` at commit `bb8fb4319f061ef22cc742ad9b2b3d5a1b5aa700`.
- Shared community rule ID: `skill.no_reason.zhixiao_baizhan`.
- Existing factor decision: `audit.finding.skill-no-reason-zhixiao-baizhan`.
- New title decision: `audit.finding.skill-no-reason-zhixiao-baizhan-title`.

## Remaining acceptance

Do not mark this maintenance unit complete yet. Required evidence is successful Validate, production Sync translation context, refreshed review-plan live context with `cf-a73e3962c7a5f8a8` absent, and the shared No Reason canonical target embedded for `知宵欺敌,百战不殆`.

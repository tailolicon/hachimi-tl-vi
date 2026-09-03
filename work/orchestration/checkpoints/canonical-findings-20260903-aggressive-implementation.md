# Canonical finding implementation — Aggressive

Finding: `cf-5f92ce6e499363dd`

- zh-CN bridge title: `以攻为守`
- JP Skill: `アグレッシブ`
- Skill ID: `203222`
- canonical target: `Aggressive`

## Implementation

- permanent hardener: `scripts/harden_aggressive_finding.py`
- regression: `tests/test_aggressive_finding_hardening.py`
- community rule: `skill.aggressive`
- terminology decision: `audit.finding.skill-aggressive`
- source scope: exact match in `text_data_dict.json`

The rule forbids historical `Lấy công làm thủ`, because pinned curation identifies the Chinese phrase as an interpretive idiom rather than title-equivalent identity. `Aggressive` preserves the direct JP katakana/English title.

Regression requires idempotence, canonical + review resolution of the real finding shape, complete removal from `active_findings`, and negative tests proving that longer text and another source file are not covered by the exact rule.

## Acceptance pending

Do not increment maintenance `completed_count` beyond 62 until Validate, production Sync translation context, and Sync translation review plan succeed on a commit containing this hardener/regression, and the live generated review context exposes `skill.aggressive` / `Aggressive` for the affected `2032201`–`2032203` entries with `cf-5f92ce6e499363dd` no longer blocking them.

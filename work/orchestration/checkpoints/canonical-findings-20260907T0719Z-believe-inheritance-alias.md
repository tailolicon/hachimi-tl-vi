# Canonical finding checkpoint — Believe inheritance alias

Finding: `cf-b20a7a534f5b700b`
Source zh-CN alias: `正因心怀信念`

## Live identity diagnosis

- The active retrospective item is an inheritance-description row in `text_data_dict.json`, category `172`, key `10950101`.
- The `1095` prefix maps to character game ID 1095, **Believe**.
- Repository canonical work has already verified Believe's JP unique Skill as `念い、信ずればこそ` and accepted the Vietnamese title **Tâm Niệm, Chính Vì Tin** for the standalone category-147 alias `正因念想，确信所在`.
- Therefore `正因心怀信念` is not a new unknown Skill identity; it is the zh-CN bridge's alternate inheritance alias for the same Believe Skill.

## Scope decision

Use a separate alias rule instead of broadening the existing standalone title rule:

- alias: `正因心怀信念`
- target: `Tâm Niệm, Chính Vì Tin`
- source: `text_data_dict.json`
- json-path prefix: `172`
- match mode: `contains`
- invalidation scope: `item`

This resolves the embedded inheritance title while preventing ordinary belief/conviction prose from being canonicalized as Believe's Skill.

## Implementation

- Hardener commit: `a7182149cb07188d7e27fa7847e8bf314fb3a9a9` (`scripts/harden_believe_omoi_shinzureba_koso_inheritance_finding.py`).
- Regression commit: `0e8342efe31ec6bb25a018d260351ec57234cd48` (`tests/test_believe_omoi_shinzureba_koso_inheritance_finding_hardening.py`).
- Regression covers idempotence, canonical/review resolution, and negative scope for category 147 and `localize_dict.json`.
- Production `Sync translation context` run `34094852494` was queued by the regression commit and must be verified before this finding is counted complete.

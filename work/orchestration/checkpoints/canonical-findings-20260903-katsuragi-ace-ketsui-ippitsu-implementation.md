# Canonical finding implementation: 決意一筆

Finding: `cf-d3211bb4e4049dd9`

- zh-CN source alias: `决意一笔`
- Skill ID: `111041`
- Verified JP title: `決意一筆`
- Character: Katsuragi Ace [雅号・墨龍]
- Canonical Vietnamese target: `Nét Bút Quyết Tâm`
- Historical target normalized: `Nét bút quyết tâm`

## Evidence and reasoning

Repository curation `work/curation/results/term-0019/claim-gpt56sol-20260826T082827Z-91c5.json` already tied `决意一笔` to Skill ID `111041`, but previously deferred because the JP title had not been verified. Current JP gameplay references identify Skill `111041` as `決意一筆`, Katsuragi Ace [雅号・墨龍]'s unique Skill. The zh-CN form is a direct simplified-script bridge and preserves the calligraphy motif. The existing Vietnamese wording `Nét bút quyết tâm` is faithful; repository skill-title policy requires consistent game-title capitalization, yielding `Nét Bút Quyết Tâm`.

## Implementation

- Hardener: `scripts/harden_katsuragi_ace_decisive_brushstroke_finding.py` at commit `7de8f3aed84d1e9950f64214b148316d2a49fd9b`.
- Regression tests: `tests/test_katsuragi_ace_decisive_brushstroke_finding_hardening.py` at commit `4e700c56e6ddaebd9907c31c237c27bd21b47eef`.
- Community rule: `skill.katsuragi_ace.ketsui_ippitsu`.
- Terminology decision: `audit.finding.skill-katsuragi-ace-ketsui-ippitsu`.
- Rule uses the complete four-character Skill title as a `contains` alias, restricted to `text_data_dict.json`, because the live finding is scoped to category-172 inheritance descriptions that contain the title inside longer text. Regression coverage proves the same alias does not resolve another file.

## Remaining acceptance

Require successful Validate, production Sync translation context, refreshed review plan, and live worker context showing `cf-d3211bb4e4049dd9` absent with the canonical rule embedded.

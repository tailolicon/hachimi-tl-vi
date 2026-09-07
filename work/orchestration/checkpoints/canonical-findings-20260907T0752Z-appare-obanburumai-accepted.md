# Canonical finding completion: Appare Obanburumai

- Finding: `cf-704e653261dc3150`
- zh-CN source: `惊叹的饕餮盛宴！`
- Verified JP identity: `あっぱれ大盤振る舞い！`
- Accepted display target: `あっぱれ大盤振る舞い！`
- Scope: exact Skill-title match in `text_data_dict.json`, item-scoped invalidation.

## Why this resolution

Repository curation already established that the zh-CN feast/gluttony wording is a localization and is not a close semantic match to the Japanese lavish-generosity idiom. The repeated inheritance rows identify the title as New Year Kitasan Black's unique Skill. Following the repository's existing JP-only proper-title treatment, the canonical target preserves the exact Japanese display title rather than freezing the historical Chinese-derived Vietnamese feast calque.

## Implementation

- Hardener: `scripts/harden_appare_obanburumai_finding.py` (`6bf8e834a3f1f05c28859b3ab9ed0a482aa0e54c`).
- Regression coverage: `tests/test_appare_obanburumai_finding_hardening.py` (`13f3df3cc6855589a6a7c4adc09ba2e2e21a574f`).
- The rule is exact-source and `text_data_dict.json` scoped, with negative tests for wrong path and prose-containing variants.

## Acceptance evidence

- Validate run `34097143642` completed successfully for the hardener + regression state.
- Production Sync run `34097119638` completed successfully for the initial canonical application.
- Production Sync run `34097143624` then completed successfully from live `main` as the unchanged proof.
- On that unchanged proof, `harden_appare_obanburumai_finding.py` reported `appare_obanburumai_hardening_changed=false` in both hardener passes.
- Canonical refresh completed with `findings=528 active=181`.
- Terminology review queue rebuilt successfully (`actionable=1891`, `conflicts=46`).
- Full context suite passed: `814 passed`.
- Final publish step reported `Context is already current.`, proving no generated-context delta remained.

## Result

The canonical pipeline accepts the exact Japanese title for this bounded Skill identity and the hardener is idempotent on production state. `cf-704e653261dc3150` is complete as canonical-maintenance work. No direct edit to `localized_data/**` was made.

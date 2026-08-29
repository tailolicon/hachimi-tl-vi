# Canonical Race finalization — complete

Completed: 2026-08-29T11:17Z

## Permanent integration

- Reconstructed a clean integration branch from live `main` because `canonical-race-hardening-20260828` had diverged substantially.
- Integrated only the eight validated permanent Race files; no TEMP inventory/debug artifacts were published to `main`.
- Permanent integration commit: `84eb9aa4f04d65d897ccfd7d536781211abc8c46`.
- Fixed the production Sync workflow's stale test path in `2a23dbfd5b30bb04547c6d9d1eb351303cc4e089` (`tests/test_review_gate_idempotence.py` -> `tests/test_translation_review_gate_idempotence.py`).

## Validation

- Clean live-main integration validation run `33249441976` passed full pytest, hardener idempotence, review-plan rebuild/no-op normalization, Python compilation, and `git diff --check`.
- Main validation after permanent integration was green.
- First successful production Sync run `33249613745` published plan `tr-p3-67f8551f7780-6290eeddf480-bea089f809-005c1551f3` with 19,520 candidates and 976 batches; 167 tests passed.
- Re-ran the same production Sync job against current `main`; attempt job `99093270565` passed 167 tests, builder reported `changed: false`, preserved the same plan id, normalized timestamp-only gate churn, and exited with `Canonical terminology and translation review plan/gate are already current.` This is the required second unchanged no-op proof.

## Representative regenerated-context checks

- `日本德比` at `text_data_dict.json` category 111 item 12 is embedded with canonical `race.tokyo_yushun` -> `Japanese Derby`, correctly flagging the historical `Japan Derby` target mismatch.
- The collapsed `京城锦标` identity at category 111 item 134 is embedded as `race.keio_hai_nisai_stakes.zhcollapse_111_134` -> `Keio Hai Nisai Stakes`, not Miyako Stakes.
- Race regression coverage additionally locks the inverse `京城锦标` category 32/item 3061 identity to `race.miyako_stakes`, race classes, G1/G2/G3 labels, racecourse scoping, category-147 ordinary objective prose negatives, and category-16 Song negatives; these tests are part of the 167-test green production Sync.
- Regenerated category-147 race-name entries such as `日本德比` retain correct target text without being given broad generic proper-race context merely because they live in objective data.

## Cleanup

- Removed `.github/workflows/validate-race-integration-temp.yml` from `canonical-race-integration-20260829` in commit `03c09c0ca43ec45e3a0a0b788b4daf1da5136a16`.
- Original Race TEMP artifacts remain excluded from `main`.

## Transition

Race is complete. The next blocking canonical-hardening domain is `canonical-training-support`, branch `canonical-training-support-hardening`, created from current post-Sync `main` (`01b467a22f397b51db01ba3412735193462a61cf`).

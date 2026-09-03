# Canonical finding checkpoint — Migraine localize context

Claim: `canonical-findings-maintenance-gpt56sol-20260903T110239Z`

Target finding: `cf-e311d621cf5334b2` (`偏头痛` → **Migraine**).

## Live finding state

The generated live canonical-findings ledger shows this finding as `status: open`, `match_mode: contains`, scoped to `localize_dict.json`, with `canonical_resolution: null` and `review_resolution: null`. Evidence is the system message `由于偏头痛，无法使用育成商品`, currently rendered with generic Vietnamese `đau nửa đầu` even though repository canon already defines the named negative Condition as **Migraine**.

## Hardening decision

Keep `common.condition.migraine` unchanged in its condition-name table scope. Add `common.condition.migraine.localize_context`, alias `偏头痛`, preferred/accepted `Migraine`, scoped only to `localize_dict.json` with `match_mode: contains`.

Add reviewed lock `audit.finding.condition-migraine-localize-context` mapping `偏头痛` to `Migraine`.

## Regression coverage

`tests/test_migraine_localize_context_finding_hardening.py` verifies idempotence, preservation of the existing table rule, resolution of the live localize finding, the reviewed lock, and non-resolution of an unquoted occurrence in `storytimeline.json`.

## Acceptance state

Implementation and regression test are published. Validate/Sync and generated-ledger persistence remain required before counting the finding complete.

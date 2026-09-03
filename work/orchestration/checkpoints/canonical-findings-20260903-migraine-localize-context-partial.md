# Canonical finding checkpoint — Migraine localize context

Claim lineage: `canonical-findings-maintenance-gpt56sol-20260903T110239Z` → `canonical-findings-maintenance-gpt56sol-20260903T1126Z`

Target finding: `cf-e311d621cf5334b2` (`偏头痛` → **Migraine**).

## Live finding state

The finding originated as `status: open`, `match_mode: contains`, scoped to `localize_dict.json`, with evidence in the system message `由于偏头痛，无法使用育成商品`. The repository already canonically names the gameplay Condition **Migraine**, so generic Vietnamese `đau nửa đầu` is not appropriate in this system-UI context.

## Hardening decision

Keep `common.condition.migraine` unchanged in its condition-name table scope. Add `common.condition.migraine.localize_context`, alias `偏头痛`, preferred/accepted `Migraine`, scoped only to `localize_dict.json` with `match_mode: contains`.

Add reviewed lock `audit.finding.condition-migraine-localize-context` mapping `偏头痛` to `Migraine`.

## Regression coverage

`tests/test_migraine_localize_context_finding_hardening.py` verifies idempotence, preservation of the existing table rule, resolution of the live localize finding, the reviewed lock, and non-resolution of an unquoted occurrence in `storytimeline.json`.

## Acceptance state

Accepted complete.

- Hardener commit: `0902c5e9ca5c7dc9aa720ddef45430aabad8f5d2`.
- Regression-test commit: `c917cd781eb07e68f7ba16c88fd1de900ed0ec26`.
- Validate run `33748663256` on maintenance checkpoint commit `41867d08ef87b5c93f421bae6eb2033598a63232` completed successfully.
- Generated-context commit `1c3dcd0a139789d331cc7361beaf9675b528eb00` persisted both canonical layers: `canonical_resolution.term_id = common.condition.migraine.localize_context`, target `Migraine`, and review decision `audit.finding.condition-migraine-localize-context`, target `Migraine`.
- The generated terminology review queue dropped the `偏头痛` canonical-finding review item and reduced open canonical findings from 220 to 219 in that generated publication.

The finding is therefore canonically hardened and persisted; continue with the next live active finding after refetching routing/ledger state.

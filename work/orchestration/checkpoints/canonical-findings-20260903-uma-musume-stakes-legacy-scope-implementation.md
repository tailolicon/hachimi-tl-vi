# Canonical finding implementation: clear legacy Uma Musume Stakes category scope

Claim: `canonical-findings-maintenance-gpt56sol-20260903T181719Z`

Finding: `cf-0dae34861911a969` (`赛马娘锦标` / JP `ウマ娘ステークス`)

## Root cause fixed

The finding hardener previously omitted `json_path_prefixes` from its replacement records, but `_upsert()` merges into existing records. A production record already carrying legacy `json_path_prefixes: [["131"]]` therefore kept that stale restriction after the hardener ran.

## Implementation

- Commit `66acb5bc9302b5b8768cb255f4da78bd45d696ee` changes both `TERM` and `DECISION` in `scripts/harden_uma_musume_stakes_component_finding.py` to explicitly write `json_path_prefixes: []`. Merge-upsert can now clear the stale category scope instead of preserving it.
- Commit `19b9eb1174bf15a408dbf87fef320df9a5b21795` updates `tests/test_uma_musume_stakes_component_finding_hardening.py` to seed the actual legacy state: both the community term and terminology decision start with `json_path_prefixes: [["131"]]`.
- The regression now requires the hardener to migrate both records to `json_path_prefixes: []`, remain idempotent on the second run, resolve the live-shape source-path-only finding to `race.uma_musume_stakes.component131 -> Uma Musume Stakes`, and keep the rule from escaping `text_data_dict.json`.

## Acceptance gate

Do not increment maintenance completion yet. Validate the final implementation head and require production context/review-plan synchronization from a head containing both commits. After those gates succeed, inspect the newly generated live review material and confirm `cf-0dae34861911a969` is no longer embedded as an active blocker before incrementing `completed_count` 39 -> 40.

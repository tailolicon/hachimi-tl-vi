# Canonical finding repair: Uma Musume Stakes live finding scope

Claim: `canonical-findings-maintenance-gpt56sol-20260903T181030Z`

Finding: `cf-0dae34861911a969` (`赛马娘锦标` / JP `ウマ娘ステークス`)

## Live diagnosis

The current generated `glossary/canonical_findings.json` still exposes this finding as blocking: status `open`, `canonical_resolution: null`, while the review resolution already locks the target to `Uma Musume Stakes`.

The existing hardener and regression were too narrow. They modeled the finding with `json_path_prefixes: [["131"]]` and emitted a category-131-only community rule. The live generated finding has no JSON-path prefix. Under `scripts/canonical_findings.py::_rule_covers_finding`, a rule with a JSON-path restriction cannot cover a finding that has no such restriction, so the production finding remained unresolved despite the earlier acceptance checkpoint.

## Durable repair

- `scripts/harden_uma_musume_stakes_component_finding.py` now matches the live finding scope: `text_data_dict.json`, contains `赛马娘锦标`, no JSON-path restriction.
- The generic `common.world.umamusume` exclusion for `赛马娘锦标` remains in place, preventing generic `赛马娘 -> Mã Nương` from firing inside this proper race-name component.
- `tests/test_uma_musume_stakes_component_finding_hardening.py` now seeds the actual live finding shape and requires `refresh_canonical_resolutions()` to produce the community resolution `race.uma_musume_stakes.component131 -> Uma Musume Stakes` and remove it from `active_findings()`.
- The negative test still proves the rule does not escape `text_data_dict.json`.

Implementation commits: `917e15f775a5890180585a6d2d41df08c9aa8426`, `e67a8ce03dfb2b8cf3d979d4c5453db465af5034`.

## Acceptance gate

Do not increment maintenance completion yet. Validate, Sync translation context, and regenerated review-plan acceptance must succeed first; then confirm the live generated finding has a non-null canonical resolution and is absent as a blocker in the regenerated plan.

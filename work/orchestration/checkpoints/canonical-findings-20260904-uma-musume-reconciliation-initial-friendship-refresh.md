# Canonical findings reconciliation — Uma Musume Stakes + regenerated Initial Friendship

## Reconciliation

`cf-0dae34861911a969` (`赛马娘锦标` / `ウマ娘ステークス`) is already materially accepted on live `main`: `glossary/ui_community_terms.json` has `race.uma_musume_stakes.component131` with `json_path_prefixes: []`, `glossary/terminology_reviews.json` carries the matching lock, and `glossary/canonical_findings.json` has a non-null community canonical resolution to `Uma Musume Stakes`. The current active review plan and `work/parallel_state.json` contain no reference to this finding. This is therefore stale continuation state, not a new completion; do **not** increment maintenance `completed_count` for it again.

## Regenerated finding repair

The live canonical-findings ledger had regenerated `cf-13f41d397ec5e6ad` (`初始羁绊槽上升`) with `canonical_resolution: null` even though this finding was previously accepted. Ran the existing production hardener `scripts/resolve_regenerated_initial_friendship_finding.py`; it restored the canonical resolution to `support.initial_friendship.effect155 -> Initial Friendship` from the existing scoped community term.

Regression validation:

```text
uv run --extra dev pytest -q tests/test_regenerated_initial_friendship_finding_resolution.py tests/test_training_support_effect_labels_hardening.py
8 passed in 0.07s
```

This is a regeneration reconciliation for a previously counted finding, so `completed_count` remains 79. Production acceptance still requires Validate + Sync translation context + Sync translation review plan from the repair head before treating the refreshed generated ledger as durable live state.

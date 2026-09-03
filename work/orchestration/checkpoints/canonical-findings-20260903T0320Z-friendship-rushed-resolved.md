# Canonical findings maintenance checkpoint

- Claim: `canonical-findings-maintenance-gpt56sol-20260903T030822Z`
- Worker: `gpt56sol-20260903T030822Z`
- Live branch: `main`
- Production Sync run: `33710879028` — success
- Validation run: `33710879070` — success

## Verified resolutions

1. `cf-55673a272df0aaae` (`牵绊值`)
   - Canonical resolution: `community` / `common.friendship_gauge.support_effects` / `Friendship Gauge`
   - Durable hardener: `scripts/harden_friendship_gauge_variant_finding.py`
   - Positive-evidence resolver only closes the finding while every evidence row remains inside the live category-155 Friendship Gauge scope.
   - Regression: `tests/test_friendship_gauge_variant_finding_hardening.py`

2. `cf-05ee17c3f625371f` (narrative prose containing `焦躁`)
   - Canonical resolution: `context_guard` / `race_state.rushed.text131` / `Rushed`
   - The gameplay Rushed term remains scoped to category 131 and no longer blocks ordinary category-128 prose.
   - Regression: `tests/test_rushed_prose_context_guard_resolution.py`

## Related pipeline repair

- Narrowed the Mecha Umamusume proper-name exclusion from broad `机械赛马娘` to evidence-bearing `机械赛马娘第三阶段`, preserving legitimate generic Mã Nương matches such as `机械赛马娘详情`.
- Validate and production Sync are green after the repair.

## Continuation

Canonical maintenance remains the highest-priority live lane because additional unresolved findings still exist. Continue with another evidence-safe context-rule blocker; do not guess deferred/uncertain proper-name identities.

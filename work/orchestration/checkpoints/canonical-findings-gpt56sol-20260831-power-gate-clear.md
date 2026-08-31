# Canonical finding checkpoint — Power context guard

- Finding: `cf-5d23e532c5359881` (`力量`)
- Canonical result: `context_guard` → `common.stat.power` → `Power`
- Narrative evidence such as `商品的力量` is excluded from the Power-stat matcher.
- Legitimate stat context such as `力量上限` remains matched as `Power`.
- Regression coverage: `tests/test_context_guard_finding_resolution.py`
- Regression commit: `d27a65dd88ed9f6f436fb1f101fc79366e9a28de`
- `sync-context` run `33359409712` completed successfully, including all hardeners, canonical finding refresh, context-guard resolution, terminology queue rebuild, and context test suite.
- Live `glossary/canonical_findings.json` now records `cf-5d23e532c5359881` with `canonical_resolution.layer = context_guard`, `term_id = common.stat.power`, `target_vi = Power`.

The systemic blocker is cleared. Workers should route from current live state and use a regenerated review plan rather than relying on stale embedded finding snapshots.

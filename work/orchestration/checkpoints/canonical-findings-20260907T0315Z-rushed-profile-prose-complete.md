# Canonical findings maintenance checkpoint — profile prose 焦躁 context guard complete

- task: `canonical-findings-maintenance`
- claim: `canonical-findings-maintenance-gpt56sol-auto11-20260907T0256Z`
- finding: `cf-47277b7ddd4be78f`
- source: `有焦躁时就会缩起来的习惯`
- evidence path: `text_data_dict.json` / `167/1070`
- previous_completed_count: `174`
- completed_count: `175`

## Diagnosis

The existing gameplay term `race_state.rushed.text131` is intentionally restricted to text-data category 131. The category-167 profile sentence uses `焦躁` descriptively (`sốt ruột`) and must not be rewritten to the player-facing race-state label `Rushed`.

## Durable implementation

- `scripts/resolve_context_guard_findings.py` registers regenerated finding `cf-47277b7ddd4be78f` against the existing `race_state.rushed.text131` guard. Commit: `093d93fed592eb64b26156f653dd8291e1cb389c`.
- `tests/test_rushed_prose_context_guard_resolution.py` now proves both category-128 narrative prose and category-167 profile prose do not match the Rushed system term, while category 131 still does; both regenerated prose findings resolve through the context guard. Commit: `f9f48a6c07c465b409b5b5c843ab0fa6e8ee74d5`.

## Production acceptance

- Validate run `34078850169`: success, including full pytest, `tlvi validate`, and `tlvi index`.
- Production Sync translation context run `34078837063`: success, including all finding hardeners, canonical refresh, context-guard resolution, context pipeline tests, and generated-context publication.
- Generated context commit: `c6d9fc93626c4f9afc98a698ee52ea0dc8bf6b72`.
- That commit gives `cf-47277b7ddd4be78f` canonical resolution `context_guard / race_state.rushed.text131 / Rushed` and removes the source from actionable canonical-finding review work.
- Open canonical findings moved from 132 to 131 in that generated context commit.

This bounded context-overmatch finding is production-validated and complete without weakening the real category-131 Rushed terminology rule.
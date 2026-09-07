# Canonical finding checkpoint — Tanino Gimlet evidence-scoped resolver validated

- Finding: `cf-46c6157b0331a647` (`神话、哲学、Vu行的发音、业余木工`).
- Resolver implementation: `scripts/resolve_scoped_canonical_overrides.py` from commit `ad94fc74858644f5f5f2a4f3dbbe3891d4333a09`.
- Regression test: `tests/test_scoped_source_bridge_override_resolution.py` from commit `6d1cd2b4ff74e29ca8f6c56062b8d4a207d56fce`.
- The resolver now permits a narrow source-bridge rule to close an aggregate finding with absent top-level scope only when an explicit reviewed lock agrees with the rule and every durable evidence row is demonstrably inside the rule scope. Any evidence outside the scope leaves the finding active.
- Validate run `34082214957` completed successfully on the regression-test commit; pytest, `tlvi validate`, and `tlvi index` all passed.
- Production Sync run `34082204703` was automatically triggered from the resolver implementation commit and is currently in progress. It must regenerate `cf-46c6157b0331a647` to `canonical_resolution.layer=source_bridge`, `term_id=source_bridge.tanino_gimlet.v_row_profile`, target `Thần thoại, triết học, phát âm các âm V, làm đồ gỗ DIY`.
- Do not complete the finding until that production Sync succeeds, live main shows the finding non-active, and a subsequent unchanged production Sync succeeds.

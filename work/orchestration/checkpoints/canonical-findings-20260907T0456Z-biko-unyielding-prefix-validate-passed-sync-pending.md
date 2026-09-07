# Canonical finding checkpoint — Biko Pegasus Unyielding Vow prefix validate passed, Sync pending

- Finding: `cf-5026b367a0d84413` (`不可动摇的热血誓言`).
- Hardener remains `scripts/harden_biko_pegasus_unyielding_prefix_finding.py`; exact player-facing variants remain locked separately as `Unyielding Vow - Sprint` and `Unyielding Vow - Mile`.
- Initial Validate run `34084687950` for commit `51ef7da281eb58af5846db40dd2a05fbdddadaa8` failed only the newly-added negative regression: 800 passed, 1 failed. The failed expectation assumed finding-side `source_paths` participate in review-decision resolution; that is not the matcher contract for this item-scoped finding.
- Regression expectation was corrected on main at commit `9127bc87d00547ea64d8221d7c597b5cf587600c` to guard against the meaningful collision: the distinct full variant source `不可动摇的热血誓言・短距离` must not receive the prefix ignore.
- Validate/check run for `9127bc87d00547ea64d8221d7c597b5cf587600c` completed successfully (`test` check run `101626816831`, workflow run `34084857217`).
- Production `Sync translation context` run `34084857240` for that commit is still pending as of this checkpoint.
- Do not increment maintenance completion yet. Resume by waiting for/inspecting production Sync `34084857240`; after success, confirm live regenerated `cf-5026b367a0d84413` is non-active via explicit ignore while exact Sprint/Mile targets remain intact, then require a second unchanged production Sync proving semantic no-op before incrementing `completed_count`.

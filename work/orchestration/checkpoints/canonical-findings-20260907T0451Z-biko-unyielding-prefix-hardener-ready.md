# Canonical finding checkpoint — Biko Pegasus Unyielding Vow prefix hardener ready

- Finding: `cf-5026b367a0d84413` (`不可动摇的热血誓言`).
- Live ledger shows this as an unresolved context-rule finding with no canonical/review resolution.
- Existing `scripts/harden_biko_pegasus_vow_finding.py` already locks the actual player-facing full Conditions exactly as `Unyielding Vow - Sprint` for `不可动摇的热血誓言・短距离` and `Unyielding Vow - Mile` for `不可动摇的热血誓言・英里`, while excluding both from the broader Passionate Vow family rule.
- Therefore `不可动摇的热血誓言` is only a lexical prefix in this finding, not a standalone player-facing Condition to canonicalize independently.
- Added item-scoped/context-scoped ignore hardener `scripts/harden_biko_pegasus_unyielding_prefix_finding.py` at commit `e5417420cf1c398824f5a0e5e7d3f09749a3726a`.
- Added regression `tests/test_biko_pegasus_unyielding_prefix_finding_hardening.py` at commit `51ef7da281eb58af5846db40dd2a05fbdddadaa8`, covering idempotence, non-active finding resolution, preservation of both exact Unyielding targets, and negative source-path scope.
- Do not increment maintenance completion until Validate and production Sync pass, live regenerated finding is non-active, and an unchanged production Sync confirms semantic no-op.
